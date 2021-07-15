# anonimizacion-texto-libre
> Free-text anonymization prototype and efficiency evaluation of different models

## Configuration

1. Create virtualenv using python3 (follow https://virtualenvwrapper.readthedocs.io/en/latest/install.html)

        virtualenv venv

2. Activate the virtualenv

        . venv/bin/activate

3. Install requirements

        pip install -r requirements.txt

4. Download a spanish base model

        python -m spacy download es_core_news_lg

5. For every anonymization you make, you will find information in a log file located in the folder `logs`.


## Main functions

#### `anonymize_doc()`
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



- If you want to anonymize text from the `third column` in the file `dataset1.csv` located in the folder `data` and save it to a file in the folder `results`:

`python tasks.py anonymize_doc --origin_path="./data" --file_name="dataset1.csv" --column_to_use=2 --save_file --destination_folder="./results"`

### Considerations
- If there's an error on the parameters you send, you will see in the console what is wrong (an suggestions to fix it).
- If you add the flag `save_file` when you anonymize free text, the file will be named with a default file name such as `texto_anonimizado.txt`.
- If you anonymize text from a csv file, the file will be named like the original file but adding `_anonimizado` at the end.


## Using it!

        Open a console and run the command
                `python [function you want to use] [parameters for that function]`


## Development

- Linting: `pre-commit install`
