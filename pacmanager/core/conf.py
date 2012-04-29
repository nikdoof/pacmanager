from modeldict import ModelDict
from .models import Setting

managerconf = ModelDict(Setting, key='key', value='value', instances=False)