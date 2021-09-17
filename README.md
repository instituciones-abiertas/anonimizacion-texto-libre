# anonimizacion-texto-libre
> Free-text anonymization prototype and efficiency evaluation of different models

## Configuration

1. Create virtualenv using python3 (follow https://virtualenvwrapper.readthedocs.io/en/latest/install.html)

        virtualenv venv

2. Activate the virtualenv

        . venv/bin/activate

3. Install requirements

        pip install -r requirements.txt

4. Download a spanish base model (we recommend the large one)

        python -m spacy download es_core_news_lg

5. For every anonymization you make, you will find information in a log file located in the folder `logs`.

6. There's a configuration file called `configuration.py` where you can find variables that are used in the code and you can modify.
## Main functions

## `anonymize_doc()`
Use this function when you want to anonymize a text, for that you have two (2) options:
- free text
- csv file

### Parameters
- `text`: Free text to be anonymized.
- `save_file`: Flag that indicates if you want to save the file.
- `origin_path`: Path to obtain the file to be anonymized.
- `file_name`: The filename from the file to be anonymized.
- `column_to_use`: Column from the file (only one) to obtain the text to be anonymized, indicate the column position (consider that the first index is zero).
- `include_titles`: Flag that indicates if the file to be anonymized include titles.
- `destination_folder`: Path where the anonymized file is going to be saved.

### Examples

- If you want to anonymize free text and see the results in the console:

`python tasks.py anonymize_doc --text="this is the text to anonymize"`



- If you want to anonymize free text and save it to a file in the folder results:

`python tasks.py anonymize_doc --text="this is the text to anonymize" --save_file --destination_folder="./results"`


- If you want to anonymize text from the `third column` in the file `dataset1.csv` located in the folder `data` and DON'T save it, the results will be shown in the console but we encourage you to save it to a file in order to analyze it better:

`python tasks.py anonymize_doc --origin_path="./data" --file_name="dataset1.csv" --column_to_use=2`



- If you want to anonymize text from the `third column` in the file `dataset1.csv` located in the folder `data` and save it to a file in the folder `results`:

`python tasks.py anonymize_doc --origin_path="./data" --file_name="dataset1.csv" --column_to_use=2 --save_file --destination_folder="./results"`

- If you want to anonymize text from the `third column` in the file `dataset1.csv` located in the folder `data` and save it to a file in the folder `results`. If the file include titles you should indicate it by using the parameter `include_titles`:

`python tasks.py anonymize_doc --origin_path="./data" --file_name="dataset1.csv" --column_to_use=2 --save_file --destination_folder="./results" --include_titles`


### Considerations
- If there's an error on the parameters you send, you will see in the console what is wrong (an suggestions to fix it).
- If you add the flag `save_file` when you anonymize free text, the file will be named with a default file name such as `texto_anonimizado.txt`.
- If you anonymize text from a csv file, the file will be named like the original file but adding `_anonimizado` at the end.

## `evaluate_efficiency()`
Use this function when you want to compare the anonymization made by the model against expected annotations. In order to achieve that, yoiu should provide a text file to be anonymized (txt) and a field with the corresponding annotations (json). You can find a JSON file example for annotations in the folder `data` => `annotations_example_eval_efficiency.json`.

### Parameters
- `origin_path`: Path to the file to be anonymized on the way to evaluate efficiency.
- `file_name`: The filename from the file to be anonymized on the way to evaluate efficiency (MUST be txt).
- `json_origin_path`: Path to the json file with the annotations from the document previously indicated.
- `json_file_name`: The filename from the json file with the annotations from the document previously indicated (MUST be json).
- `destination_folder`: Path where the comparison between the anonymization and the annotations will be saved.
- `results_file_name`: The file name where the comparison results will be added (it will be a csv file). The default file name will be obtain from the configuration file and informed in the console.

### Results
On the results file you will find four columns indicating: 
- Entidad: entity that should be included in the list of entities declared in the configuration file.
- Modelo: amount (integer) of entities recognized by the model.
- Esperado: amount (integer) of entities identified by the annotations (this is the ideal amount of entities that should be recognized by the model).
- Efectividad: model efficiency (percentage).

The efficiency is calculated by:
Modelo / Esperado * 100

Based on that, if the model detects more entities that expected then the efficiency could be bigger than 100% (weird isn't it?). That means that there are missing entities in the annotations or that the model is marking as entities things which are not. Whatever the case, it should be reviewed.
### Examples

- If you want to evaluate the efficiency for `testing_data/test_eval_ef.txt`, using annotations from `testing_data/annotations_test_eval_ef.json` and saving the results in the folder `results` without setting a `results_file_name`:

`python tasks.py evaluate_efficiency --origin_path="./testing_data" --file_name="test_eval_ef.txt" --json_origin_path="./testing_data" --json_file_name="annotations_test_eval_ef.json" --destination_folder="./results"`

- If you want to evaluate the efficiency for `testing_data/test_eval_ef.txt`, using annotations from `testing_data/annotations_test_eval_ef.json` and saving the results in the folder `results` with the file name `results_evaluate_efficiency`:

`python tasks.py evaluate_efficiency --origin_path="./testing_data" --file_name="test_eval_ef.txt" --json_origin_path="./testing_data" --json_file_name="annotations_test_eval_ef.json" --destination_folder="./results" --results_file_name=results_evaluate_efficiency`

### Considerations
- If there's an error on the parameters you send, you will see in the console what is wrong (an suggestions to fix it).
- To see all entities that are being detected check `ENTITIES_LIST` in `configuration.py`.

## Using it!

        Open a console and run the command
                `python [function you want to use] [parameters for that function]`


## Development

- Linting: `pre-commit install`
