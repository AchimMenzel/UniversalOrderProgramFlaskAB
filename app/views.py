from flask.ext.appbuilder.actions import action
from flask import render_template, request
from flask.ext.appbuilder.models.sqla.interface import SQLAInterface
from flask.ext.appbuilder import BaseView, expose
from flask_appbuilder.fields import AJAXSelectField
from flask_appbuilder.fieldwidgets import Select2AJAXWidget, Select2SlaveAJAXWidget
from app import appbuilder, db, app
from .models import table_supplier, table_orders, table_orderline, table_category, table_product, table_price
from flask_mail import Message, Mail
from flask.ext.babel import lazy_gettext as _
from .modifiedClasses.views_modified import ModelViewModified
from flask import redirect
from sqlalchemy import text

class PriceAdmin(ModelViewModified):
    #base table
    datamodel = SQLAInterface(table_price)
    # title for the listview
    list_title = _('Prices')
    #columns for label
#    label_columns = {'product.name':_('Product'),'product':_('Product'),'date':_('Date'), 'price':_('Price')}
    label_columns = {'product.category.name':'Kategorie', 'product.name':'Produkt','date':'Datum', 'price':'Preis'}
    #columns shown in listview
    list_columns = ['product.category.name', 'product.name', 'date', 'price']
    #how the list is ordered
    order_columns = ['product.category.name', 'product.name', 'date', 'price']
    #columns in the addform
    add_columns = ['product', 'price', 'date']
    #columns in the editform
    edit_columns = ['product', 'price', 'date']
    #columns in the showform
    show_columns = ['id', 'product.category.name', 'product', 'date']
    #title of showform
    show_title = _('Price Details')
    #title of addform
    add_title = _('Price Add')
    #title of editform
    edit_title = _('Price Edit')
    #title of the list
    list_title = _('PriceAdmin')

    #base order in the beginning
    base_order = ('date', 'desc')

    #how many entries are shown on one page
    page_size = 100

class ProductAdmin(ModelViewModified):
    #base table
    datamodel = SQLAInterface(table_product)
    # title for the listview
    list_title = _('Products')
    # columns for label
#    label_columns = {'category.name':_('Category'),'category':_('Category'),'name':_('Product Name')}
    label_columns = {'category.name':'Kategorie','name':'Produktname','price':'letzter Preis'}
    #the related view (subtable that is in relation)
    related_views = [PriceAdmin]
    #columns shown in listview
    list_columns = ['category.name', 'name']
    #how the list is ordered
    order_columns = ['category.name', 'name']
    #columns in the addform
    add_columns = ['category', 'name']
    #columns in the editform
    edit_columns = ['category', 'name']
    #columns in the showform
    show_columns = ['id', 'category', 'name']
    #title of showform
    show_title = _('Product Details')
    #title of addform
    add_title = _('Product Add')
    #title of editform
    edit_title = _('Product Edit')

    page_size = 100

    base_order = ('name', 'asc')

class CategoryAdmin(ModelViewModified):
    #base table
    datamodel = SQLAInterface(table_category)
    # columns for label
    label_columns = {'name':_('Category')}
    # title for the listview
    list_title = _('Categories')
    #the related view (subtable that is in relation)
    related_views = [ProductAdmin]
    #columns shown in listview
    list_columns = ['name']
    #how the list is ordered
    order_columns = ['name']
    #columns in the addform
    add_columns = ['name']
    #columns in the editform
    edit_columns = ['name']
    #columns in the showform
    show_columns = ['id', 'name']
    #title of showform
    show_title = _('Category Details')
    #title of addform
    add_title = _('Category Add')
    #title of editform
    edit_title = _('Category Edit')

    page_size = 100

    base_order = ('name', 'asc')
    
class OrderlineAdmin(ModelViewModified):
    #base table
    datamodel = SQLAInterface(table_orderline)
    # title for the listview
    list_title = _('Orderlines')
    # columns for label
    label_columns = {'category.name': _('Category'),'product.name':_('Product'), 'pricePerUnit.price':_('Price per Unit'),'number':_('Units'),'total_cost':_('Cost'),'comment':_('Comment'),'category':_('Category'),'order':_('Order'), 'units':_('Units')}
    #special AJAX-fields
    add_form_extra_fields = {
                    'category': AJAXSelectField('Category',
                    datamodel=datamodel,
                    col_name='category',
                    widget=Select2AJAXWidget(endpoint='/orderlineadmin/api/column/add/category')),

                    'product': AJAXSelectField('product',
                    datamodel=datamodel,
                    col_name='product',
                    widget=Select2SlaveAJAXWidget(master_id='category',
                    endpoint='/orderlineadmin/api/column/add/product?_flt_0_categoryId={{ID}}')),
    }

    #same AJAX-fields for edit as for add
    edit_form_extra_fields = add_form_extra_fields
    #columns shown in listview
    list_columns = ['category.name', 'product.name', 'pricePerUnit.price', 'units', 'total_cost', 'comment']
    #how the list is ordered
    order_columns = ['category.name', 'product.name', 'pricePerUnit.price', 'units', 'total_cost', 'comment']
    #columns in the addform
    add_columns = ['order', 'category', 'product', 'number', 'comment']
    #columns in the editform
    edit_columns = ['order', 'category', 'product', 'number', 'comment']
    #columns in the showform
    show_columns = ['id', 'order', 'category', 'product', 'pricePerUnit', 'units', 'total_cost', 'comment']
    #title of showform
    show_title = _('Orderline Details')
    #title of addform
    add_title = _('Orderline Add')
    #title of editform
    edit_title = _('Orderline Edit')

    page_size = 1000

    base_order = ('name', 'asc')

    #@action("export_pdf","Export data to PDF", "Do you want to?","fa-rocket", multiple=True, single=False)
    #def export_pdf(self, item):

        #PrintOrder(item).pdf_export()
        #return redirect(request.referrer)

    #action function to send email
    @action("send_mail", "Send mail with this order", "Do you want to?", "fa-rocket", multiple=True, single=False)
    def create_mail(self, item):
        try:
            msg = PrintOrder(item).send_mail()
            return render_template('emailSuccess.html', base_template=appbuilder.base_template, appbuilder=appbuilder, msg=msg), 200
        except:
            return render_template('emailFailure.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 500

    def write_sum(self, numberTotal, priceTotal, id):
    #writes the sums of number and prices of table orderline into table orders
        #create a sql-query object
        sqlUpdate = text('update table_orders set total_number= :numberTotal, total_price= :priceTotal where id = :id')
        #write into database
        db.engine.execute(sqlUpdate, numberTotal=numberTotal, priceTotal=priceTotal, id=id)

    #action function to update prices of the goods of the displayed order
    @action("update_prices","Update prices", "Do you want to?", "fa-rocket", single=False)
    def refresh_prices(self, item):
    #writes the appropriate price from table_price with the newest date into table_orderline

        #if the view is empty exit
        if not item:
            return redirect(request.referrer)

        #variables for write_sum function
        numberTotal = 0
        priceTotal = 0

        for line in item:
            #create a sql-query object
            sqlSelect = text('select id from table_price where productId= :productId order by date desc limit 1')
            #get one line from sql-query as a dictionary
            newestPriceId = db.engine.execute(sqlSelect, productId=line.productId).first()
            newPriceExists = False

            if line.pricePerUnit != None:
                if (newestPriceId["id"]) != line.pricePerUnit.id:
                    # create another sql-query object
                    try:
                        # there must be a price for the product
                        sqlUpdate = text('update table_orderline set priceId= :priceId where id = :id')
                        # write priceId into database
                        db.engine.execute(sqlUpdate, priceId=newestPriceId["id"], id=line.id)
                        newPriceExists = True
                        #get newest price
                        sqlSelectPrice = text('select price from table_price where id= :newestPriceId')
                        newestPrice = db.engine.execute(sqlSelectPrice, newestPriceId=newestPriceId["id"]).first()
                    except:
                        # there is no price for the product
                        print("Es gab einen Fehler beim Sql Update des neuesten Preises für "
                              + line.product.category.name + " - " + line.product.name + ". " +
                              "Wahrscheinlich ist für das Produkt kein Preis vorhanden.")
            else:
                # create another sql-query object
                try:
                #there must be a price for the product
                    sqlUpdate = text('update table_orderline set priceId= :priceId where id = :id')
                    #write priceId into database
                    db.engine.execute(sqlUpdate, priceId=newestPriceId["id"], id=line.id)
                    newPriceExists = True
                    # get newest price
                    sqlSelectPrice = text('select price from table_price where id= :newestPriceId')
                    newestPrice = db.engine.execute(sqlSelectPrice, newestPriceId=newestPriceId["id"]).first()
                except:
                #there is no price for the product
                    print("Es gab einen Fehler beim Sql Update des neuesten Preises für "
                          + line.product.category.name + " - " + line.product.name + ". " +
                          "Wahrscheinlich ist für das Produkt kein Preis vorhanden.")

            #summing up some data for function write_sum to calculate the overall number and cost
            if type(line.number) == float:
                numberTotal += line.number
                if newPriceExists:
                    priceTotal += round(newestPrice["price"] * line.number, 2)
                else:
                    if type(line.total_price()) == float:
                        priceTotal += line.total_price()

        self.write_sum(numberTotal, priceTotal, item[0].orderId)
        return redirect(request.referrer)

class PrintOrder():
    #delivers all data of one order and a pdf export and mail function

    def __init__(self, item):
        #the information about the supplier and the order
        baseItem = item[0]
        self.client = baseItem.order.supplier.client
        self.address = baseItem.order.supplier.address
        self.telephone = baseItem.order.supplier.telephone
        self.email = baseItem.order.supplier.email
        self.emailText = baseItem.order.supplier.emailText
        self.emailSubject = baseItem.order.supplier.emailSubject
        self.comment = baseItem.order.comment
        self.target_date = baseItem.order.target_date
        self.target_time = baseItem.order.target_time
        self.total_number = baseItem.order.total_number
        self.total_price = baseItem.order.total_price

        #the orders in detail
        self.orders = []
        for line in item:
            orderLine = {}
            orderLine["category"] = line.product.category.name
            orderLine["product"] = line.product.name
            orderLine["comment"] = line.comment
            if type(line.number) == float:
                orderLine["number"] = line.number
            else:
                #do not integrate orders without number
                continue
            if type(line.total_price()) == float:
                orderLine["total_price"] = line.total_price()
            else:
                #if type is None then integrate the empty string
                orderLine["total_price"] = ""
            self.orders.append(orderLine)

    def simplePrint(self):
        #simply demonstrate the attributes
        print(self.client)
        print(self.address)
        print(self.telephone)
        print(self.email)
        print(self.emailText)
        print(self.comment)
        print(self.target_date)
        print(self.target_time)
        print(self.total_number)
        print(self.total_price)
        print(self.orders)

    def pdf_export(self):
        #to be implemented
        self.simplePrint()

    def send_mail(self):
        #sends an email to a certain recipient
        mail = Mail(app)

        #build the body of the email
        mailOrderText = "\n\n"
        for line in self.orders:
            mailOrderText += "{0:8.2f} - ".format(line["number"]) + line["category"] + "_" + line["product"] + \
                             "... " + line["comment"] + "\n"
        mailOrderText += "\n" + self.comment

        msg = Message(self.emailSubject + ", " + str(self.target_date) + " " + self.target_time,
            body=self.emailText + mailOrderText,
            sender="broyjoerg@web.de",
            recipients=[self.email])

        #print(msg)
        mail.send(msg)
        return msg


class OrdersAdmin(ModelViewModified):
    #base table
    datamodel = SQLAInterface(table_orders)
    #the related view (subtable that is in relation)
    related_views = [OrderlineAdmin]
    # title for the listview
    list_title = _('Orders')
    # columns for label
    label_columns = {'supplier.client':_('Supplier'), 'target_date':_('Target date'), 'total_number':_('Total number'), 'tot_price':_('Total price'),'supplier':_('Supplier')}
    #columns shown in listview
    list_columns = ['supplier.client', 'target_date', 'total_number', 'tot_price']
    #how the list is ordered
    order_columns = ['supplier.client', 'target_date', 'target_time', 'total_number', 'tot_price']
    #columns in the addform
    add_columns = ['supplier', 'target_date', 'target_time', 'comment']
    #columns in the editform
    edit_columns = ['supplier', 'target_date', 'target_time', 'comment']
    #columns in the showform
    show_columns = ['id', 'supplier.client', 'target_date', 'target_time', 'total_number', 'tot_price', 'comment']
    #title of showform
    show_title = _('Orders Details')
    #title of addform
    add_title = _('Orders Add')
    #title of editform
    edit_title = _('Orders Edit')
    #title of the list
    list_title = _('OrdersAdmin')

    #how many entries are shown on one page
    page_size = 100

    #base order in the beginning
    base_order = ('date', 'desc')

class SupplierAdmin(ModelViewModified):
    #base table
    datamodel = SQLAInterface(table_supplier)
    #the related view (subtable that is in relation)
    related_views = [OrdersAdmin]
    # title for the listview
    list_title = _('Suppliers')
    # columns for label
    label_columns = {'client':_('Client'),'email':_('Email'),'address':_('Adress'),'telephone':_('Telephone'),'email':_('Email adress'),'emailText':_('Email Text')}
    #columns shown in listview
    list_columns = ['client', 'email']
    #how the list is ordered
    order_columns = ['client', 'email', 'id']
    #columns in the addform
    add_columns = ['client', 'address', 'telephone', 'email', 'emailText', 'emailSubject', 'comment']
    #columns in the editform
    edit_columns = ['client', 'address', 'telephone', 'email', 'emailText', 'emailSubject', 'comment']
    #columns in the showform
    show_columns = ['id', 'client', 'address', 'telephone', 'email', 'emailText', 'emailSubject', 'comment']
    #title of showform
    show_title = _('Supplier Details')
    #title of addform
    add_title = _('Supplier Add')
    #title of editform
    edit_title = _('Supplier Edit')

    page_size = 100

    base_order = ('client', 'asc')


db.create_all()

#register the views here
appbuilder.add_view(SupplierAdmin, 'SupplierAdmin', category = 'Orders',category_label=_('Orders'), label = _('Supplier'))
appbuilder.add_view_no_menu(OrdersAdmin)
appbuilder.add_view_no_menu(OrderlineAdmin)
appbuilder.add_view(CategoryAdmin, 'CategoryAdmin', category = 'Products',category_label=_('Products'), label = _('Category'))
appbuilder.add_view(ProductAdmin, 'ProductAdmin', category = 'Products',category_label=_('Products'), label = _('Product'))
appbuilder.add_view_no_menu(PriceAdmin)

@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404
