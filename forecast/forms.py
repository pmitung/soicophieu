from re import M
from django import forms
from django.forms import CharField, ClearableFileInput, EmailInput, HiddenInput, ModelForm, NumberInput, TextInput, Textarea, URLInput
from matplotlib import widgets
from . models import Comment, ForecastPrice, UserProfile
from django import forms
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget
from ckeditor.widgets import CKEditorWidget
from ckeditor.fields import RichTextFormField


movement_choices = (
    (1, "Tăng"),
    (0, "Đi ngang"),
    (-1, "Giảm")
)


attrs_value = {}

class UserForecastForm(forms.Form):
    forecast_movement_T1 = forms.ChoiceField(
        choices=movement_choices, 
        # label='Dự báo ngày {{form_data.form_forecast_date_T1|safe}}',
        label_suffix='',
        widget=forms.Select,
        # (attrs={'class':'{% if 1 > 2 %} form-select mt-2 mb-4 {% else %} form-form {% endif %}'  , 'disabled':'True'}),
        required=True 
        )
    forecast_movement_T3 = forms.ChoiceField(
        choices=movement_choices, 
        # label='Dự báo ngày T+4 {{form_data.form_forecast_date_T3|safe}}',
        label_suffix='',
        widget=forms.Select(attrs={'class':'form-select mt-2 mb-4'}),
        required=True 
        )

class FollowerForm(forms.Form):
    user_id = forms.CharField(label_suffix='', max_length=150, required=False, widget=forms.HiddenInput)
    follower_id = forms.CharField(label_suffix='', max_length=150, required=False, widget=forms.HiddenInput)

class TickerFollowForm(forms.Form):
    ticker_id = forms.CharField(label_suffix='', max_length=15, required=False, widget=HiddenInput)
    follower_id = forms.CharField(label_suffix='', max_length=150, required=False, widget=HiddenInput)

class TickerUnfollow(forms.Form):
    ticker_id = forms.CharField(label_suffix='', max_length=15, required=False, widget=HiddenInput)
    follower_id = forms.CharField(label_suffix='', max_length=150, required=False, widget=HiddenInput)

class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['display_name', 'bio', 'phone', 'zalo_room', 'avatar']
        widgets = {
            'display_name': TextInput(attrs={'placeholder': 'Tên hiển thị'}),
            'bio': RichTextFormField(config_name="default"),
            'phone': NumberInput(attrs={'placeholder': 'Số điện thoại'}),
            'zalo_room': TextInput(attrs={'placeholder': 'Zalo'}),
            'avatar':forms.FileInput(attrs={'type':'file', 'id':'formFile'})
        }


class SearchForm(forms.Form):
    ticker_id = forms.CharField(label_suffix='', max_length=15, required=True, widget=forms.TextInput(attrs={'placeholder':'Tìm mã cổ phiếu', 'id':'ticker-search'}))
    
