from odoo import api, fields, models, _
from odoo.exceptions import UserError
class MagenestTestCaseStep(models.Model):
    _description = 'Test Step'
    _name = 'testcase.step'

    name = fields.Char('Test Step', required=True, translate=True)
    test_id = fields.Many2one('testcase.testcase', string='Test Case')

class MagenestTestCase(models.Model):
    """
       Model for test cases management.
       """
    _name = 'testcase.testcase'
    _description = 'Test Case'
    _order = "sequence"
    _inherit = ['mail.thread']

    CRITICALITY_SELECTION = [
        ('0', 'General'),
        ('1', 'Important'),
        ('2', 'Very important'),
        ('3', 'Critical')
    ]

    criticality = fields.Selection(CRITICALITY_SELECTION, 'Criticality')

    TYPE_SELECTION = [
        ('0', 'Functional'),
        ('1', 'Integration'),
        ('2', 'Performance'),
        ('3', 'Unit')
    ]

    type = fields.Selection(TYPE_SELECTION, 'Type')

    STATE_SELECTION = [
        ('0', 'Passed'),
        ('1', 'Failed'),
        ('2', 'NA'),
        ('3', 'Fixed')
    ]

    name = fields.Char('Test Case', required=True, translate=True)

    state = fields.Selection(STATE_SELECTION, 'State')

    approved = fields.Boolean('Approved', default=False)

    user_id = fields.Many2one('res.users', 'Assigned to', track_visibility='onchange')

    step_ids = fields.One2many('testcase.step', 'test_id')

