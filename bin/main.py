import hashlib

def get_invoices(db, date_begin, date_end):
    s = """select order_id from wpdn_wcpdf_invoice_number where date between '%s' and '%s'""" % (date_begin, date_end)
    db.cursor.execute(s)
    result = [i[0] for i in db.cursor.fetchall()]
    return result


def get_items_for_invoice(db, invoice_number):
    s = """select * from wpdn_woocommerce_order_items where order_id = %s""" % invoice_number
    db.cursor.execute(s)
    result = db.cursor.fetchall()
    to_return = dict()
    for i in result:
        to_return[i[0]] = dict()
        to_return[i[0]]['order_item_name'] = i[1]
        to_return[i[0]]['order_item_type'] = i[2]

    return {'items': to_return}


def get_data_for_item(db, item_id):
    s = """select meta_key, meta_value from wpdn_woocommerce_order_itemmeta where order_item_id = %s""" % item_id
    db.cursor.execute(s)
    result = db.cursor.fetchall()
    to_return = dict()
    for i in result:
        to_return[i[0]] = i[1]

    return to_return


def get_item_mentor_id(db, product_id):
    s = """select meta_value from wpdn_postmeta where post_id = %s and meta_key = '_sku'""" % product_id
    db.cursor.execute(s)
    result = db.cursor.fetchall()[0][0]
    return {'mentor_id': result}


def get_additional_invoice_data(db, invoice_id):
    s = """select meta_value from wpdn_postmeta where meta_key = '_wcpdf_invoice_number' and post_id = %d""" \
            % invoice_id
    db.cursor.execute(s)
    result = db.cursor.fetchall()
    if len(result) > 0:
        to_return = {'invoice_number': result[0][0]}
    else:
        return {'invoice_number': None}

    s = """select meta_value from wpdn_postmeta where meta_key = '_shipping_first_name' and post_id = %d""" \
        % invoice_id
    db.cursor.execute(s)
    to_return['name'] = db.cursor.fetchall()[0][0]

    s = """select meta_value from wpdn_postmeta where meta_key = '_shipping_last_name' and post_id = %d""" \
        % invoice_id
    db.cursor.execute(s)
    to_return['name'] += ' ' + db.cursor.fetchall()[0][0]

    s = """select meta_value from wpdn_postmeta where meta_key = '_billing_company' and post_id = %d""" \
        % invoice_id
    db.cursor.execute(s)
    to_return['company'] = db.cursor.fetchall()[0][0]

    s = """select meta_value from wpdn_postmeta where meta_key = '_billing_address_1' and post_id = %d""" \
        % invoice_id
    db.cursor.execute(s)
    to_return['address'] = db.cursor.fetchall()[0][0]

    s = """select meta_value from wpdn_postmeta where meta_key = '_billing_address_2' and post_id = %d""" \
        % invoice_id
    db.cursor.execute(s)
    to_return['address'] += ' ' + db.cursor.fetchall()[0][0]

    s = """select meta_value from wpdn_postmeta where meta_key = '_billing_city' and post_id = %d""" \
        % invoice_id
    db.cursor.execute(s)
    to_return['city'] = db.cursor.fetchall()[0][0]

    s = """select meta_value from wpdn_postmeta where meta_key = '_billing_state' and post_id = %d""" \
        % invoice_id
    db.cursor.execute(s)
    to_return['state'] = db.cursor.fetchall()[0][0]

    s = """select meta_value from wpdn_postmeta where meta_key = '_billing_phone' and post_id = %d""" \
        % invoice_id
    db.cursor.execute(s)
    to_return['phone'] = db.cursor.fetchall()[0][0]

    s = """select meta_value from wpdn_postmeta where meta_key = '_billing_email' and post_id = %d""" \
        % invoice_id
    db.cursor.execute(s)
    to_return['email'] = db.cursor.fetchall()[0][0]

    client_code = hashlib.md5()
    client_code.update(to_return['name']+to_return['phone'])
    client_code = client_code.hexdigest()
    to_return['client_code'] = client_code

    return to_return


def invoices_to_json(db, date_start, date_finish):
    invoices = dict()
    for i in get_invoices(db, date_start, date_finish):
        invoices[i] = dict()

    for i in invoices:
        invoices[i] = get_items_for_invoice(db, i)
        invoices[i].update(get_additional_invoice_data(db, i))
    for i in invoices:
        number_of_products = 0
        for item_id in invoices[i]['items']:
            invoices[i]['items'][item_id].update(get_data_for_item(db, item_id))
            if '_product_id' in invoices[i]['items'][item_id]:
                invoices[i]['items'][item_id].update(get_item_mentor_id(db,
                                                                        invoices[i]['items'][item_id]['_product_id']))
                number_of_products += 1
            if 'method_id' in invoices[i]['items'][item_id]:
                invoices[i]['items'][item_id]['mentor_id'] = "767"
        invoices[i]['number_of_products'] = number_of_products
    invoices = {i: invoices[i] for i in invoices if len(invoices[i]['items']) != 0}
    invoices = {'invoices': invoices, 'number_of_invoices': len(invoices)}
    return invoices


if __name__ == "__main__":
    pass
