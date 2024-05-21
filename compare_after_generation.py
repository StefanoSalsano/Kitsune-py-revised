import pandas as pd

miraidf = pd.read_csv('Mirai_dataset.csv', header=None, index_col=0, nrows=100)
df = pd.read_csv('output.csv', header=None, index_col=0, nrows=100)

for i in range(0,7):
  for j in range(1,116):

    if df.at[i+1,j]-miraidf.at[i,j] != 0 :
        print(i,j,df.at[i+1,j]-miraidf.at[i,j],df.at[i+1,j],miraidf.at[i,j])
