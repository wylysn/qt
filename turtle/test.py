import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from Account import Account

# df = pd.DataFrame(columns=['buytime','buycount','buyprice'])
final_date2 = datetime.strptime('2022-9-30 10:38:00', '%Y-%m-%d %H:%M:%S')
# df.loc[len(df)] = [final_date2, 3, 4]
# df.loc[len(df)] = [final_date2, 1, 8]
# print(df)
# buycount = df['buycount'].sum()
# buyprice = df['buyprice'].sum()
# df=df.drop(index=df.index)
# print(df)

# ac = Account(100000, 0.1, None, None)
# ac.printinfo()

ac = Account(1000000, 10000, 0.1, None, None)
ac.buy(final_date2, 1, 1, 1000, 10000)