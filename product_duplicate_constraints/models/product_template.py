# -*- coding: utf-8 -*-
import itertools
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    assembly_code_ref = fields.Char(string="Reference Assembly Code", copy=False)

    @api.onchange('template_code')
    def _onchange_assembly_code(self):
        for product in self:
            if product.template_code and product.is_goods:
                code_ref = product.assembly_code_name_get()
                product.update({'assembly_code_ref': code_ref})

    @api.model
    def assembly_code_name_get(self):
        assembly_code_unique = False
        for res in self:
            if res.template_code and res.is_goods and not assembly_code_unique:
                res_name_strip = res.template_code.strip()
                res_name_split = res_name_strip.split(sep=" ")
                assembly_code_unique = ''.join(code.lower() for code in res_name_split)
        return assembly_code_unique

    @api.constrains('template_code')
    def _check_assembly_code(self):
        for res in self:
            if res.assembly_code_ref and res.template_code:
                product_id = self.env['product.template'].search_count(
                    [('assembly_code_ref', '=', res.assembly_code_ref),
                     ('company_id', '=', res.company_id.id)])
                if product_id and product_id > 1:
                    raise ValidationError(_("Hello Buddy, An Assembly Code Must Be Unique"))
                else:
                    return False


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, values):
        product_template = self.env['product.template']
        assembly_reference = False
        if values.get('product_tmpl_id', False) and values.get('attribute_value_ids', False) and not assembly_reference:
            if product_template.browse(values.get('product_tmpl_id')) and \
                    product_template.browse(values.get('product_tmpl_id')).mapped('is_goods') and \
                    product_template.browse(values.get('product_tmpl_id')).mapped('template_code'):
                template_attributes = product_template.browse(
                    values.get('product_tmpl_id')).mapped('attribute_line_ids').mapped('value_ids')
                attributes_explode = self.product_attribute_explode(values['attribute_value_ids'])
                if attributes_explode and template_attributes:
                    attributes_name = template_attributes.filtered(lambda x: x in attributes_explode).mapped('name')
                    template_code = product_template.browse(values.get('product_tmpl_id')).template_code
                    attribute_join = ''.join(ref + " " for ref in attributes_name)
                    assembly_reference = template_code + " " + attribute_join

        if assembly_reference:
            values.update({'default_code': assembly_reference})
        return super(ProductProduct, self).create(values)

    @api.multi
    def product_attribute_explode(self, attribute_value_ids):
        attribute_value_object = self.env['product.attribute.value']
        variant_matrix = [
            attribute_value_object.browse(value_ids)
            for value_ids in itertools.product(*(attrib_value[2]
                                                 for attrib_value in attribute_value_ids))]
        return variant_matrix


