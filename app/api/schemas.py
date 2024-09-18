from marshmallow import Schema, fields, validate, ValidationError, validates
from app.main.data import COUNTRIES, CURRENCIES, STAR_RATINGS


class CafeSchema(Schema):
    """ Schema for validating Cafe data. """
    name = fields.String(required=True, validate=validate.Length(min=2, max=30))
    map_url = fields.String(required=True, validate=validate.URL())
    city = fields.String(required=True, validate=validate.Length(min=2, max=25))
    country = fields.String(required=True, validate=validate.Length(min=2, max=20))
    coffee_price = fields.String(
        required=True,
        validate=validate.Regexp(r'^\d+(\.\d{1,2})?$', error='Enter a digit in string format'),
        error_messages={"invalid": "Enter a digit in string format"}
    )
    currency = fields.String(required=True, validate=validate.Length(max=10))
    wifi_strength = fields.Integer(validate=validate.Range(min=0, max=5))
    seats = fields.Integer(required=True, validate=validate.Range(min=0))
    has_sockets = fields.Boolean(required=True)
    has_toilet = fields.Boolean(required=True)
    images = fields.String(validate=validate.Length(max=350))
    full_review = fields.String(validate=validate.Length(min=3, max=300))
    full_rating = fields.Integer(required=True, validate=validate.Range(min=1, max=5))

    @validates('country')
    def validate_country(self, value):
        """ Validates that the country value matches the allowed format. """
        if not any(value == choice[0] for choice in COUNTRIES):
            raise ValidationError('Invalid country format. Check documentation.')

    @validates('currency')
    def validate_currency(self, value):
        """ Validates that the currency value matches the allowed format. """
        if not any(value == choice[0] for choice in CURRENCIES):
            raise ValidationError('Invalid currency format. Use currency symbol.')

    @validates('wifi_strength')
    def validate_wifi_strength(self, value):
        """ Validates that the wifi_strength value is within the allowed range. """
        if not any(str(value) == choice[0] for choice in STAR_RATINGS):
            raise ValidationError('Invalid wifi-strength format. Required format: 0 - 5')

    @validates('full_rating')
    def validate_full_rating(self, value):
        """ Validates that the full_rating value is within the allowed range. """
        if not any(str(value) == choice[0] for choice in STAR_RATINGS[1:]):
            raise ValidationError('Invalid full-rating format. Required format: 1 - 5')
