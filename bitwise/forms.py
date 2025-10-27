from django import forms

class NumbersForm(forms.Form):
    a = forms.FloatField(label="a")
    b = forms.FloatField(label="b")
    c = forms.FloatField(label="c")
    d = forms.FloatField(label="d")
    e = forms.FloatField(label="e")

    def clean(self):
        cleaned = super().clean()
        # All are numeric by definition (FloatField), but we’ll also flag negatives
        negatives = [k for k, v in cleaned.items() if v is not None and v < 0]
        cleaned["has_negatives"] = len(negatives) > 0
        cleaned["negative_fields"] = negatives
        return cleaned
