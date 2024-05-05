from odoo import fields, models, api

class customers_product_info(models.Model):
    _name = "custproduct.info.model"
    _description = "Product to customer"

    productserialnumber=char(string="Product serial no")
    productid=Many2one("product.info.model",string="Model")

