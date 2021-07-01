# anonimizacion-texto-libre
Free-text anonymization prototype and efficiency evaluation of different models

## Configuration

1. Create virtualenv using python3 (follow https://virtualenvwrapper.readthedocs.io/en/latest/install.html)

        virtualenv venv

2. Activate the virtualenv

        . venv/bin/activate

3. Install requirements

        pip install -r requirements.txt

4. Download a spanish base model

        python -m spacy download es_core_news_lg
