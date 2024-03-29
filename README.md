# readly-get
Permet de sauvegarder une copie d'une publication Readly.

Le but est de pouvoir lire une publication sur un support non compatible avec les applications fournies par Readly. 
Il est évident que les publications ne doivent en aucun cas être conservées une fois la lecture terminée ou lorsque votre abonnement ne vous permet plus de la lire. 
 
## readly_get.py
Permet de sauvegarder une copie d'une publication Readly. 
 
### Utilisation
```
usage: readly_get.py [-h] [--token TOKEN] [--output-folder OUTPUT_FOLDER] [--pattern PATTERN] [--image-format {jpeg,webp}] [--quality QUALITY] [--container-format {pdf,cbz}] [--low-quality] [--dpi DPI]
                     [--user-agent USER_AGENT] [--pause SECONDS] [--max-dl MAX_DL] [--no-clean] [--get-articles] [--get-articles-only] [--create-token] [--version]
                     [url]

Script to save a Readly publication.

positional arguments:
  url                   URL of the desired publication or publication_id.

options:
  -h, --help            show this help message and exit
  --token TOKEN         Authentication token or file containing the token. Default="auth_token".
  --output-folder OUTPUT_FOLDER, -o OUTPUT_FOLDER
                        Folder to save your publication. Default="DOWNLOADS".
  --pattern PATTERN     Pattern to name your file (available: "title", "issue", "date"). Default="title - issue (date)".
  --image-format {jpeg,webp}, -i {jpeg,webp}
                        Image format saved (available: "jpeg", "webp"). Default="jpeg".
  --quality QUALITY, -q QUALITY
                        Image quality (100 = best quality). Default="85".
  --container-format {pdf,cbz}, -c {pdf,cbz}
                        Output file type (available: "cbz", "pdf"). Default="pdf".
  --low-quality         Get default low quality images instead of HQ images.
  --dpi DPI             Image DPI (0 = original DPI). Default="300".
  --user-agent USER_AGENT
                        User-agent to use.
  --pause SECONDS, -p SECONDS
                        Make a pause (in seconds) between two pages. Default="0"
  --max-dl MAX_DL       Max number of issues to download. Default="1".
  --no-clean            Don't delete the temp folder where the images are stored.
  --get-articles        Also download attached articles. Use with "--no-clean" option, or files will be deleted.
  --get-articles-only   Download only attached articles (no image). Won't create PDF / CBZ file. Will force "--no-clean" option.
  --create-token        Create a new token.
  --version             Current version.
```

L'`URL` attendue est au format `https://go.readly.com/{folders}/{magazine_id}/{publication_id}` ou `https://go.readly.com/{folders}/{magazine_id}` voire `https://{pays}.readly.com/products/magazine/nom-du-magazine`. On peut aussi donner directement l'identifiant de la publication ou du magazine (24 caractères). 
Si c'est l'URL ou l'identifiant d'un magazine, c'est la publication la plus récente qui sera récupérée. 
Il est possible de mettre un chemin vers un fichier texte qui contient une liste d'URL. Toutes les lignes de ce fichier seront traitées. Il est possible de générer cette liste avec `readly_latest.py`. 

L'option `--token TOKEN` (optionnelle) permet de préciser le token d'API du compte Readly. On peut mettre en paramètre soit le token, soit un fichier qui contient le token. 
Si le token n'est pas renseigné, il est lu du fichier de config `auth_token`. 
Si le token n'est pas disponible dans ce fichier de config, il est demandé et sera sauvegardé dans `auth_token`. 

L'option `--output-folder "FOLDER"` ou `-o FOLDER` (optionnelle) permet de préciser le répertoire dans lequel seront stockés les fichiers. 
Si l'option n'est pas renseignée, le répertoire `DOWNLOADS` sera utilisé. 

L'option `--pattern "PATTERN"` (optionnelle) permet de choisir la façon dont les fichiers seront nommés. 
Les champs disponibles sont : `title` (le titre du magazine), `issue` (le nom de ce numéro), `date` (la date de publication). 
Si l'option n'est pas renseignée, le pattern utilisé sera `"title - issue (date)"`. 

L'option `--image-format {jpeg|webp}` ou `-i {jpeg|webp}` (optionnelle) permet de choisir le format des images qui seront utilisées. 
Les valeurs possibles sont : `jpeg` et `webp`. 
Si l'option n'est pas renseignées, le format `jpeg` sera utilisé. 
 
L'option `--quality QUALITY` ou `-q QUALITY` (optionnelle) permet de choisir la qualité de l'image. 
La valeur attendue doit être en `100` (meilleure qualité) et `0` (pire qualité). 
Si l'option n'est pas renseignées, la qualité `70` sera utilisé. 

L'option `--container-format {cbz|pdf}` ou `-c {cbz|pdf}` (optionnelle) permet de choisir le format du fichier dans lequel seront regroupées les images. 
Les valeurs possibles sont : `cbz` et `pdf`. 
Si l'option n'est pas renseignées, le format `pdf` sera utilisé. 

L'option `--low-quality` permet de récupérer les images en basse qualité. Attention, elles ne sont pas toujours disponibles. 

L'option `--dpi DPI` (optionnelle) permet de choisir le DPI des images enregistrées. 
Si l'option n'est pas renseignées, le DPI original des images sera conservé. 

L'option `--user-agent "USERAGENT"` (optionnelle) permet de choisir un user-agent spécifique à utiliser. 
Si l'option n'est pas renseignées, le user-agent `okhttp/3.12.1` sera utilisé. 

L'option `--pause SECONDS` ou `-p SECONDS` (optionnelle) permet de définir une pause (en secondes) à respecter entre chaque fichier récupéré. 
Si l'option n'est pas renseignées, aucune pause (`0`) ne sera appliquée. 

L'option `--max-dl` permet de définir combien de publications seront téléchargées au maximum dans le cas où l'URL correspond à une série. 
Si l'option n'est pas renseignée, une seule publication sera téléchargée (la plus récente). 

L'option `--no-clean` (optionnelle) permet de ne pas supprimer le répertoire temporaire dans lequel les images sont sauvegardées. 
Si l'option n'est pas renseignées, le répertoire temporaire sera supprimé après création du fichier CBZ ou PDF. 

L'option `--get-articles` (optionnelle) permet de dire que l'on souhaite télécharger aussi les articles qui sont parfois attachés à des publications. Attention à bien utiliser l'option `--no-clean`, sinon les articles seront supprimés en même temps que le répertoire temporaire. 
Si l'option n'est pas renseignées, les articles ne sont pas téléchargés. 

L'option `--get-articles-only` (optionnelle) permet de dire que l'on souhaite télécharger uniquement les articles qui sont parfois attachés à des publications. L'utilisation de cette option implique que les images ne seront pas téléchargées et le répertoire temporaire ne sera pas supprimé. Aucun fichier CBZ ou PDF ne sera généré.  

L'option `--create-token` (optionnelle) permet de faire une demande de nouveau token. L'utilisation de cette option implique qu'aucune autre action ne sera effectuée. 

L'option `--version` (optionnelle) permet d'afficher la version actuelle de l'application et de la comparer à la dernière version disponible. 
  
  
### Exemples 
#### Télécharger un magazine
```
python readly_get.py https://go.readly.com/magazines/category/it-technology/5e1f18a6d9e840630147fd25/60267250adeadd000d8c86e6
```
qui est l'équivalent de 
```
python readly_get.py --token auth_token --output-folder DOWNLOADS --pattern "title - issue (date)" --image-format jpeg --quality 70 --container-format pdf https://go.readly.com/magazines/category/it-technology/5e1f18a6d9e840630147fd25/60267250adeadd000d8c86e6
```
Le script va lire le token dans le fichier `auth_token`. Il va ensuite récupérer toutes les pages du magazine au format JPEG (qualité 70), puis compiler un PDF qui aura comme nom `Python & C++ for Beginners - February 2021 (2021-02-18).pdf`. 
Le répertoire temporaire sera supprimé. 

#### Télécharger le dernier numéro d'un magazine
```
python readly_get.py https://go.readly.com/magazines/category/it-technology/5e1f18a6d9e840630147fd25
```
Dans cet exemple, l'identifiant de la publication n'est pas mentionné, seul l'identifiant du magazine l'est. 
Le script va regarder quelle est la dernière publication disponible pour ce magazine et va la télécharger. 

#### Télécharger les articles d'un magazine
```
python readly_get.py --get-articles-only https://go.readly.com/magazines/category/news_politics/55e012198ea57fe8d300002e
```
Le script va récupérer uniquement les articles liés au magazine. 

#### Télécharger un magazine en CBZ qui utilise des images WEBP
```
python readly_get.py --image-format webp --quality 70 --container-format cbz https://go.readly.com/magazines/category/comics/5326c3fd01704d0ca7000034
```
L'avantage du format d'image WEBP est qu'il permet d'avoir une meilleure qualité d'image pour une taille inférieure à une image JPEG équivalente. 
Malheureusement, le format PDF ne permet pas d'inclure ce format d'image. Il faut donc utiliser le format `CBZ` en tant que container. 
  
   
   
   
## readly_latest.py
Permet de lister les publications Readly les plus récentes. 
 
### Utilisation
```
usage: readly_latest.py [-h] [--type TYPE] [--limit NUMBER] [--countries COUNTRIES] [--languages LANGUAGES]
                        [--categories CATEGORIES] [--output OUTPUT_FILE]

Script to display Readly latest publications.

optional arguments:
  -h, --help            show this help message and exit
  --type TYPE, -t TYPE  Type of publications ("magazines", "newspapers" or "magazines,newspapers").
                        Default="magazines,newspapers".
  --limit NUMBER, -i NUMBER
                        Number of issues per type. Default=25
  --countries COUNTRIES, -c COUNTRIES
                        Coutries of publications (2-letters format) coma separated. Default="" (all coutries).
  --languages LANGUAGES, -l LANGUAGES
                        Languages of publications (2-letters format) coma separated. Default="" (all languages).
  --categories CATEGORIES, -a CATEGORIES
                        Categories of publications coma separated. Default="" (all categories).
  --output OUTPUT_FILE, -o OUTPUT_FILE
                        Output to a file.
```

L'option `--type TYPE` ou `-t TYPE` (optionnelle) permet préciser de le type de publications recherchées. 
Les valeurs possibles sont : `magazines`, `newspapers` ou `"magazines,newspapers"`.
Si l'option n'est pas renseignées, le types utilisé sera `"magazines,newspapers"`. 

L'option `--limit NUMBER` ou `-i NUMBER` (optionnelle) permet de limiter le nombre de publications à retourner. 
Si l'option n'est pas renseignées, `25` publications (par type) seront retournées. 

L'option `--countries COUNTRIES` ou `-c COUNTRIES` (optionnelle) permet de limiter les pays d'origine des publications. Il faut indiquer les codes pays (2 caractères). 
On peut mettre plusieurs pays, séparés par des virgules. Par exemple pour filtrer sur tous les pays anglophones : `--countries "US,GB,IE,AU,NZ,CA"`.
Si l'option n'est pas renseignées, aucun filtre de pays ne sera appliqué. 

L'option `--languages LANGUAGES` ou `-l LANGUAGES` (optionnelle) permet de limiter les langues d'origine des publications. Il faut indiquer les codes langue (2 caractères). 
On peut mettre plusieurs langues, séparées par des virgules. Par exemple pour filtrer sur les publications en anglais ou en français : `--languages "en,fr"`.
Si l'option n'est pas renseignées, aucun filtre de langue ne sera appliqué. 

L'option `--categories CATEGORIES` ou `-a CATEGORIES` (optionnelle) permet de limiter les catégories des publications. 
Si l'option n'est pas renseignées, aucun filtre de catégorie ne sera appliqué. 

L'option `--output OUTPUT_FILE` ou `-o OUTPUT_FILE` (optionnelle) permet d'enregistrer le résultat de la requète dans le fichier `OUTPUT_FILE`. 
Ce fichier pourra ensuite être utilisé en entrée de `readly_get.py`. 
Si l'option n'est pas renseignées, le résultat sera affiché sur la sortie standard. 

### Exemples 
#### Lister les magazines en langue anglaise et les enregistrer dans un fichier
```
python readly_latest.py --languages en --output liste.txt
```

## Installation 
### Prérequis
- [Python 3.9+](https://www.python.org/downloads/windows/) (non testé avec les versions précédentes)
- pip

### Windows
- En ligne de commande, on clone le repo : 
```
git clone https://github.com/izneo-get/readly-get.git
cd readly-get
```
- (optionnel) On crée un environnement virtuel Python dédié : 
```
python -m venv env
env\Scripts\activate
```
- On installe les dépendances : 
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
- On peut exécuter le script :
```
python readly_get.py
```
- (optionnel) On quitte le l'environnement virtuel : 
```
deactivate
```

Si vous avez une erreur à cause d'une librairie SSL manquante, vous pouvez essayer de l'installer avec la commande :  
```
pip install pyopenssl
```
Si cela ne fonctionne pas, vous pouvez télécharger [OpenSSL pour Windows](http://gnuwin32.sourceforge.net/packages/openssl.htm). 
