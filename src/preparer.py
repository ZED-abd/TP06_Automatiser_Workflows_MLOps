import os
import yaml
import pandas as pd
from sklearn.model_selection import train_test_split

p = yaml.safe_load(open('params.yaml', encoding='utf-8'))['preparation']
df = pd.read_csv('data/transactions.csv')

train, test = train_test_split(df, test_size=p['test_size'],
                               random_state=p['random_state'])

os.makedirs('data/prepare', exist_ok=True)
train.to_csv('data/prepare/train.csv', index=False)   # sortie 1
test.to_csv('data/prepare/test.csv', index=False)     # sortie 2
print('preparation :', len(train), 'lignes train /', len(test), 'lignes test')
