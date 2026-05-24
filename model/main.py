from logger import setup_model_logger
from predict import run_inference


if __name__ == "__main__":
    setup_model_logger()
    run_inference()

# The model is far far to be perfect, check the train.py commentary for more infos, but it'll not be perfect at all since
# I don't have the ressources to get the best model possible.
