import datetime
import json


class Winmentor:
    def __init__(self):
        self.invoice_body = ''
        self.transfer_body = ''
        self.partners_body = ''
        self.transfer_count = 0

    def create_header(self, number_of_invoices):
        current_time = datetime.datetime.now()
        header = '[InfoPachet]\nAnLucru=%s\nLunaLucru=%s\nTipdocument=FACTURA IESIRE\nTotalFacturi=%d\n' % \
                 (str(current_time.year), str(current_time.month), number_of_invoices)
        return header

    def create_header_invoice(self, invoice_json, invoice_counter):
        current_time = datetime.datetime.now()
        header = '[Factura_%d]\n' % invoice_counter
        header += 'NrDoc=%s\nSerieCarnet=CAR\nData=%s\n' % (invoice_json['invoice_number'], str(current_time.day) + '.' + str(current_time.month) +
                                                            '.' + str(current_time.year))
        header += 'CodClient=%s\n' % invoice_json['client_code']
        if invoice_json['company'] == '':
            header += 'Denumire=%s\n' % invoice_json['name'].upper()
        else:
            header += 'Denumire=%s\n' % invoice_json['company'].upper()
        header += 'TotalArticole=%d\n' % invoice_json['number_of_products']
        header += 'Operat=d\n'
        return header

    def get_header_item(self, products_counter, products_json):
        header_item = 'Item_%d=%s;BUC;' % (products_counter, products_json['mentor_id'])
        header_item += '%s;%s;ONLINE;\n' % (products_json['_qty'],
                                            str(float(products_json['_line_total'])/float(products_json['_qty'])))
        header_item += 'Item_%d_TVA=%s\n' % (products_counter, products_json['_line_tax'])
        return header_item

    def get_transfer_json_item(self, products_json, transfer_dict):
        if products_json['mentor_id'] not in transfer_dict:
            transfer_dict[products_json['mentor_id']] = {'qty': 0, 'price':
                                                         str(float(products_json['_line_total'])
                                                             / float(products_json['_qty']))}

        transfer_dict[products_json['mentor_id']]['qty'] += int(products_json['_qty'])
        return transfer_dict

    def create_export_file_from_json(self, invoice_json):
        header = self.create_header(invoice_json['number_of_invoices'])
        invoice_counter = 0
        self.invoice_body += header
        ex_partners = json.load(open('./bin/ex_partners', 'r'))
        for invoice in invoice_json['invoices']:
            invoice_counter += 1
            header_invoice = self.create_header_invoice(invoice_json['invoices'][invoice], invoice_counter)
            products = invoice_json['invoices'][invoice]['items']
            header_item = '[Items_%d]\n' % invoice_counter
            self.invoice_body += header_invoice
            products_counter = 0
            for product in products:
                if '_product_id' in products[product]:
                    products_counter += 1
                    header_item += self.get_header_item(products_counter, products[product])

            discount_item = ''
            for product in products:
                if 'discount_amount' in products[product]:
                    products_counter += 1
                    discount_item = 'Item_%d=%s;LEI;1;-%s\nItem_%d_TVA=-%s\n' % (products_counter,
                                                                                 'mentor_cod_discount',           # TODO
                                                                                 products[product]['discount_amount'],
                                                                                 products_counter,
                                                                                 products[product]['discount_amount_tax'])

            shipping_item = ''
            for product in products:
                if 'method_id' in products[product]:
                    if products[product]['method_id'] == 'fan_courier' and products[product]['cost'] != '0.00':
                        products_counter += 1
                        shipping_item = 'Item_%d=%s;LEI;1;12.61\nItem_%d_TVA=2.39\n' % (products_counter,
                                                                                        products[product]['mentor_id'],
                                                                                        products_counter)

            self.invoice_body += header_item
            self.invoice_body += discount_item
            self.invoice_body += shipping_item
            if invoice_json['invoices'][invoice]['client_code'] not in ex_partners:
                self.partners_body += self.get_partners_structure(invoice_json['invoices'][invoice])
                ex_partners.append(invoice_json['invoices'][invoice]['client_code'])

        transfer_items = {}
        products_counter = 0
        for invoice in invoice_json['invoices']:
            products = invoice_json['invoices'][invoice]['items']
            for product in products:
                if '_product_id' in products[product]:
                    products_counter += 1
                    transfer_items = self.get_transfer_json_item(products[product], transfer_items)

        transfer_items_str = ''
        item_counter = 0
        for i in transfer_items:
            item_counter += 1
            transfer_items_str += 'Item_%d=%s;BUC;' % (item_counter, i)
            transfer_items_str += '%s;%s;DACIA;\n' % (transfer_items[i]['qty'],
                                                        transfer_items[i]['price'])

        self.transfer_body += self.get_transfer_header(len(transfer_items))
        self.transfer_body += transfer_items_str

        json.dump(ex_partners, open('./bin/ex_partners', 'w'))

    def write_to_file(self):
        open('export/export_facturi.txt', 'w').write(self.invoice_body)
        open('export/export_transfer.txt', 'w').write(self.transfer_body)
        open('export/partner.txt', 'w').write(self.partners_body)

    def get_transfer_header(self, products_counter):
        current_time = datetime.datetime.now()
        transfer_header = '[InfoPachet]\nAnLucru=%s\nLunaLucru=%s\nTipdocument=TRANSFER\nTotalTransferuri=%d\n' % \
                          (str(current_time.year), str(current_time.month), 1)
        transfer_header += '[Transfer_1]\n'
        transfer_number = json.load(open('./bin/remember_data', 'r'))['last_transfer_number']
        json.dump({'last_transfer_number': transfer_number + 1}, open('./bin/remember_data', 'w'))
        transfer_header += 'NrDoc=%d\n' % transfer_number
        transfer_header += 'SerieCarnet=TRON\nData=%s\n' % (
            str(current_time.day) + '.' + str(current_time.month) +
            '.' + str(current_time.year))
        transfer_header += 'GestDest=ONLINE\n'
        transfer_header += 'TotalArticole=%d\n' % products_counter
        transfer_header += 'Operat=d\n'
        transfer_header += 'Observatii=fact online\n'
        transfer_header += '[Items_1]\n'
        return transfer_header

    def get_partners_structure(self, invoice_json):
        partners_header = '[ParteneriNoi_%s]\n' % invoice_json['client_code']
        if invoice_json['company'] == '':
            partners_header += 'Denumire=%s\n' % invoice_json['name'].upper()
        else:
            partners_header += 'Denumire=%s\n' % invoice_json['company'].upper()
        partners_header += 'Localitate=%s\n' % invoice_json['city']
        partners_header += 'Tara=Romania\n'
        partners_header += 'Judet=%s\n' % invoice_json['state']
        partners_header += 'Adresa=%s\n' % invoice_json['address']
        if invoice_json['company'] == '':
            partners_header += 'Clasa=PF\n'
        else:
            partners_header += 'Clasa=PJ\n'
        partners_header += 'CodIntern=%s\n' % invoice_json['client_code']
        partners_header += 'Telefon=%s\n' % invoice_json['phone']
        partners_header += 'Email=%s\n' % invoice_json['email']
        if invoice_json['company'] == '':
            partners_header += 'PersoanaFizica=Da\n'
        else:
            partners_header += 'PersoanaFizica=Nu\n'
        return partners_header
