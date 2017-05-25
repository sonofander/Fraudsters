# coding: utf-8
import pandas as pd
import datetime as dt
import cPickle as pickle

def model_load():
    return pickle.load(open('model.p', 'rb'))

def data_clean(readin, dummies):
    point = pd.read_json(readin)
    orig = point.copy()
    datecols = ['approx_payout_date', 'event_created', 'event_end', 'event_start', 'event_published', 'user_created']

    convert = lambda x: dt.datetime.fromtimestamp(x)
    df_copy = point.copy()
    for i in datecols:
        df_copy[i]=df_copy[i].apply(pd.to_numeric)
        df_copy[i]=df_copy[i].apply(convert)

    df_copy['created_date'] = df_copy['event_created'].dt.date
    df_copy['started_date'] = df_copy['event_start'].dt.date
    # df['published_date'] = df['event_published'].dt.date
    df_copy['approx_payout_day'] = df_copy['approx_payout_date'].dt.date
    #Creating new column where TRUE if all dates are equal
    date_df = df_copy[['created_date','started_date']]
    date_df['all_equal'] = ((date_df['created_date']==date_df['started_date']))
    #(date_df[‘created_date’]==date_df[‘published_date’]) &
    # created_started = date_df[date_df['all_equal']==True]
    # sum(created_started['Fraud'])/float(len(created_started))
    point['all_equal'] = date_df['all_equal']

    keep_col = ['all_equal', 'body_length', 'channels', 'country', 'currency', \
                'delivery_method', 'event_created', 'event_end', 'event_published', 'event_start', \
                'fb_published', 'gts', 'has_analytics', 'has_logo', 'listed', \
                'name_length', 'num_order', 'num_payouts', 'org_facebook', 'org_twitter', \
                'payout_type', 'sale_duration', 'sale_duration2', 'show_map', 'user_age', \
                'user_created', 'user_type', 'venue_country', 'venue_latitude', 'venue_longitude', \
                'venue_state']
    point =  point[keep_col]
    for col in dummy_dict:
        values = dummy_dict[col]
        for value in values:
            point[(value + '_' + col)] = int(point[col] == value)
        point.pop(col)
    return (point, orig)

def pred_send(points, model):
    point, orig = points
    p = model.predict_proba(point.values)[0][1]
    if p > 2.0/3:
        risk = 'High'
    elif p > 1.0/3:
        risk = 'Medium'
    else:
        risk = 'Low'
    print 'Risk Level: ' + risk + ' with probability of ' + str(p*100) + '%'

if __name__ == '__main__':
    m = model_load()
    model = m[0]
    dummy_dict = m[1]
    readin = 'example.json'
    point, orig = data_clean(readin, dummy_dict)
    pred_send((point, orig), model)
    # return orig
