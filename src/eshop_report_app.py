import datetime

from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)
app.config["DEBUG"] = True

ENDPOINT_PATH = '/api/v1/e-shop_report'

COMMISSIONS_TAB_PATH = '../data/commissions.csv'
ORDER_LINES_TAB_PATH = '../data/order_lines.csv'
ORDERS_TAB_PATH = '../data/orders.csv'
PROD_PROMOS_TAB_PATH = '../data/product_promotions.csv'
PRODS_TAB_PATH = '../data/products.csv'
PROMOTIONS_TAB_PATH = '../data/promotions.csv'

LANDING_MSG = 'Nothing to see here! The path to the endpoint is /api/v1/e-shop_report.'
DATE_PARSE_ERR_MSG = 'Unable to interpret the year, month and day provided. Please ' \
                     'ensure that you provide all four digits for the year, e.g., ' \
                     '2019 rather than 19.'
MISSING_PARAM_ERR_MSG = 'Please specify the date for which you would like to see ' \
                        'sales statistics. The date must be provided by assigning ' \
                        'values to three query parameters: "y" for the year, "m" for ' \
                        'the month and "d" for the day. '


@app.route('/')
def handle_root_request():
    """
    Return a message to inform the user that there's nothing at the root and to
    provide the path to the endpoint.
    :return: A message containing the path to the endpoint
    """
    return LANDING_MSG


@app.route(ENDPOINT_PATH)
def handle_eshop_report_request():
    """
    This function handles requests to the endpoint. If the provided query parameters
    can be parsed into a date, this function computes and returns the business
    statistics in JSON.
    :return: The business statistics in JSON if valid date parameters are given,
    error messages otherwise.
    """
    if 'y' in request.args and 'm' in request.args and 'd' in request.args:
        try:
            date = datetime.date(int(request.args['y']),
                                 int(request.args['m']),
                                 int(request.args['d']))
        except (ValueError, TypeError):
            return DATE_PARSE_ERR_MSG
        return jsonify(_compute_endpoint_response_dict(date))
    else:
        return MISSING_PARAM_ERR_MSG


def _compute_endpoint_response_dict(date):
    """
    For a given date, compute the business statistics described in the specification.

    :param date: A datetime.date object
    :return: A dictionary containing the business statistics described in the
    specification.
    """
    # Read the CSV files that do not have a date column.
    order_lines_df = pd.read_csv(ORDER_LINES_TAB_PATH)

    # Read the CSV files that do have a date column and filter by date.
    commissions_df = pd.read_csv(COMMISSIONS_TAB_PATH, parse_dates=['date'])
    orders_df = pd.read_csv(ORDERS_TAB_PATH, parse_dates=['created_at'])
    prod_promos_df = pd.read_csv(PROD_PROMOS_TAB_PATH, parse_dates=['date'])

    # Convert the date columns from NumPy datetime format to vanilla Python datetime
    # format.
    commissions_df['date'] = commissions_df['date'].dt.date
    orders_df['created_at'] = orders_df['created_at'].dt.date
    prod_promos_df['date'] = prod_promos_df['date'].dt.date

    # Filter out rows corresponding to orders that weren't placed on the given date.
    commissions_df = commissions_df[commissions_df['date'] == date]
    orders_df = orders_df[orders_df['created_at'] == date]
    prod_promos_df = prod_promos_df[prod_promos_df['date'] == date]

    # Initialise the combined DataFrame by joining the orders DataFrame to the
    # order_lines DataFrame.
    combined_df = orders_df.merge(order_lines_df, left_on='id', right_on='order_id')
    combined_df = combined_df.merge(commissions_df, on='vendor_id')
    combined_df = combined_df.merge(prod_promos_df, on='product_id')

    # Compute statistics that don't require commission information.
    customers = combined_df['customer_id'].nunique()
    total_discount_amount = combined_df['discounted_amount'].sum()
    items = int(combined_df['quantity'].sum())
    order_total_avg = combined_df['total_amount'].mean()
    discount_rate_avg = combined_df['discount_rate'].mean()

    combined_df['commission_amount'] = combined_df['rate'] * combined_df['total_amount']

    commission_total = combined_df['commission_amount'].sum()
    avg_commission_per_order = combined_df['commission_amount'].mean()

    total_commission_per_promo_df = combined_df.groupby('promotion_id').sum()
    total_commission_per_promo_dict = total_commission_per_promo_df[
        'commission_amount'].to_dict()

    return {'customers': customers,
            'total_discount_amount': total_discount_amount,
            'items': items,
            'order_total_avg': order_total_avg,
            'discount_rate_avg': discount_rate_avg,
            'commissions': {
                'promotions': total_commission_per_promo_dict,
                'total': commission_total,
                'order_average': avg_commission_per_order
            }}


if __name__ == '__main__':
    app.run()
