from django.shortcuts import render, redirect
from django.conf import settings
from .forms import NumbersForm
from pymongo import MongoClient
from datetime import datetime

def get_collection():
    client = MongoClient(settings.MONGO_URL)
    db = client[settings.MONGO_DB]
    return db[settings.MONGO_COLLECTION]

def index(request):
    context = {"form": NumbersForm()}
    if request.method == "POST":
        form = NumbersForm(request.POST)
        if form.is_valid():
            a = form.cleaned_data["a"]
            b = form.cleaned_data["b"]
            c = form.cleaned_data["c"]
            d = form.cleaned_data["d"]
            e = form.cleaned_data["e"]

            original = [a, b, c, d, e]
            has_negatives = form.cleaned_data["has_negatives"]
            negative_fields = form.cleaned_data["negative_fields"]

            # average and > 50?
            avg = sum(original) / len(original)
            avg_gt_50 = avg > 50

            # count positives and bitwise parity check
            positives = [x for x in original if x > 0]
            positive_count = len(positives)
            is_positive_count_even = (positive_count & 1) == 0  # bitwise requirement

            # values > 10 sorted
            over_ten_sorted = sorted([x for x in original if x > 10])

            # Prepare results
            results = {
                "original": original,
                "over_ten_sorted": over_ten_sorted,
                "average": avg,
                "avg_gt_50": avg_gt_50,
                "positive_count": positive_count,
                "positive_count_parity": "even" if is_positive_count_even else "odd",
                "has_negatives": has_negatives,
                "negative_fields": negative_fields,
            }

            # Save to MongoDB (input + output)
            try:
                coll = get_collection()
                doc = {
                    "timestamp": datetime.utcnow(),
                    "inputs": {"a": a, "b": b, "c": c, "d": d, "e": e},
                    "results": results,
                }
                coll.insert_one(doc)
                context["saved"] = True
            except Exception as e:
                context["saved"] = False
                context["save_error"] = str(e)

            context["form"] = form
            context["results"] = results
            return render(request, "bitwise/index.html", context)

        else:
            context["form"] = form
            return render(request, "bitwise/index.html", context)

    return render(request, "bitwise/index.html", context)

def entries(request):
    try:
        coll = get_collection()
        docs = list(coll.find().sort("timestamp", -1))
    except Exception as e:
        docs = []
        error = str(e)
        return render(request, "bitwise/entries.html", {"docs": docs, "error": error})

    return render(request, "bitwise/entries.html", {"docs": docs})
