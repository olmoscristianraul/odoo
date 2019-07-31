# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import stdnum.ar


class ResPartner(models.Model):

    _inherit = 'res.partner'

    l10n_ar_cuit = fields.Char(
        compute='_compute_l10n_ar_cuit', string="CUIT", help='Computed field that returns cuit or nothing if this one'
        ' is not set for the partner')
    l10n_ar_formatted_cuit = fields.Char(
        compute='_compute_l10n_ar_formatted_cuit', string="Formated CUIT", help='Computed field that will convert the'
        ' given cuit number to the format {person_category:2}-{number:10}-{validation_number:1}')

    l10n_ar_gross_income_number = fields.Char('Gross Income Number')
    l10n_ar_gross_income_type = fields.Selection(
        [('multilateral', 'Multilateral'), ('local', 'Local'), ('no_liquida', 'No Liquida')],
        'Gross Income Type', help='Type of gross income: exempt, local, multilateral')
    l10n_ar_afip_responsability_type_id = fields.Many2one(
        'l10n_ar.afip.responsability.type', string='AFIP Responsability Type', index=True, help='Defined by AFIP to'
        ' identify the type of responsabilities that a person or a legal entity could have and that impacts in the'
        ' type of operations and requirements they need.')
    l10n_ar_special_purchase_document_type_ids = fields.Many2many(
        'l10n_latam.document.type', 'res_partner_document_type_rel', 'partner_id', 'document_type_id',
        string='Other Purchase Documents', help='Set here if this partner can issue other documents further than'
        ' invoices, credit notes and debit notes')

    @api.depends('l10n_ar_cuit')
    def _compute_l10n_ar_formatted_cuit(self):
        """ This will add some dash to the CUIT number in order to show in his natural format:
        {person_category}-{number}-{validation_number} """
        for rec in self.filtered('l10n_ar_cuit'):
            rec.l10n_ar_formatted_cuit = stdnum.ar.cuit.format(rec.l10n_ar_cuit)

    @api.depends('vat', 'l10n_latam_identification_type_id')
    def _compute_l10n_ar_cuit(self):
        """ We add this computed field that returns cuit or nothing ig this one is not set for the partner. This
        Validation can be also done by calling ensure_cuit() method that returns the cuit or error if this one is not
        found."""
        for rec in self:
            commercial_partner = rec.commercial_partner_id
            if rec.l10n_latam_identification_type_id.l10n_ar_afip_code == '80':
                rec.l10n_ar_cuit = rec.vat
            # If the partner is outside Argentina then we return the defined
            # country cuit defined by AFIP for that specific partner
            elif commercial_partner.country_id and commercial_partner.country_id != self.env.ref('base.ar'):
                rec.l10n_ar_cuit = commercial_partner.country_id[
                    commercial_partner.is_company and 'l10n_ar_cuit_juridica' or 'l10n_ar_cuit_fisica']

    @api.constrains('vat', 'l10n_latam_identification_type_id')
    def check_vat(self):
        """ Since we validate more documents than the vat for Argentinian partners (CUIT, CUIL, DNI) we
        extend this method in order to process it.
        """
        # NOTE by the moment we include the CUIT (VAT) validation also here because we extend the messages
        # errors to be more friendly to the user. In a future when Odoo improve the base_vat message errors
        # we can change this method and use the base_vat.check_vat_ar method.s
        l10n_ar_partners = self.filtered(lambda x: x.l10n_latam_identification_type_id.l10n_ar_afip_code)
        l10n_ar_partners.l10n_ar_identification_validation()
        return super(ResPartner, self - l10n_ar_partners).check_vat()

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + ['l10n_ar_afip_responsability_type_id']

    def ensure_cuit(self):
        """ This method is a helper that returns the cuit number is this one is defined if not raise an UserError.

        CUIT is not mandatory field but for some Argentinian operations the cuit is required, for eg  validate an
        electronic invoice, build a report, etc.

        This method can be used to validate is the cuit is proper defined in the partner """
        self.ensure_one()
        if not self.l10n_ar_cuit:
            raise UserError(_('No CUIT configured for partner [%i] %s') % (self.id, self.name))
        return self.l10n_ar_cuit

    def _get_afip_responsabilities(self):
        """ Return the list of values of the selection field. """
        return [
            ('1', 'IVA Responsable Inscripto'),
            ('3', 'IVA no Responsable'),
            ('4', 'IVA Sujeto Exento'),
            ('5', 'Consumidor Final'),
            ('6', 'Responsable Monotributo'),
            ('8', 'Proveedor del Exterior'),
            ('9', 'Cliente del Exterior'),
            ('10', 'IVA Liberado – Ley Nº 19.640'),
            ('13', 'Monotributista Social'),
        ]

    def _get_validation_module(self):
        self.ensure_one()
        if self.l10n_latam_identification_type_id.l10n_ar_afip_code in ['80', '86']:
            return stdnum.ar.cuit
        elif self.l10n_latam_identification_type_id.l10n_ar_afip_code == '96':
            return stdnum.ar.dni

    def l10n_ar_identification_validation(self):
        for rec in self.filtered('vat'):
            module = rec._get_validation_module()
            if not module:
                continue
            try:
                module.validate(rec.vat)
            except module.InvalidChecksum:
                raise ValidationError(_('The validation digit is not valid for "%s"') % rec.l10n_latam_identification_type_id.name)
            except module.InvalidLength:
                raise ValidationError(_('Invalid length for "%s"') % rec.l10n_latam_identification_type_id.name)
            except module.InvalidFormat:
                raise ValidationError(_('Only numbers allowed for "%s"') % rec.l10n_latam_identification_type_id.name)
            except Exception as error:
                raise ValidationError(repr(error))
