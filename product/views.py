import os
import json
import logging
import traceback
import pandas as pd

from django.db.models import Q
from django.shortcuts import render
from product.models import Product, Category, Brand
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

logger = logging.getLogger(__name__)


@csrf_exempt
def search(request):
    try:
        value = request.GET['value']

        ret_data = []
        keys_mapping = {'name': 'name', 'category': 'category__name', 'sub-category': 'category__sub_category',
                        'brand': 'brand__name', 'model': 'model', 'composition': 'composition', 'UOM': 'UOM'}

        products = Product.objects.filter(Q(name__icontains=value) | Q(category__name__icontains=value) |
                                      Q(category__sub_category__icontains=value) | Q(brand__name__icontains=value) |
                                      Q(model__icontains=value) | Q(composition__icontains=value) |
                                      Q(UOM__icontains=value)).values(*keys_mapping.values()).distinct()

        for product in products:
            temp_dict = {}
            for key in keys_mapping.keys():
                temp_dict[key] = product[keys_mapping[key]]
            ret_data.append(temp_dict)

        return JsonResponse(json.dumps(ret_data), safe=False)

    except Exception as error:
        logger.error(error)
        logger.error(traceback.format_exc())
        return HttpResponseBadRequest(str(error))


@csrf_exempt
def upload(request):
    try:
        excel = request.FILES['file']
        ret_data = []
        lines = []
        cmd = """"curl -s -H "Content-Type: application/json" -XPOST localhost:9200/products/mobiles/_bulk 
                    --data-binary "@/tmp/bulk.json"""

        df = pd.read_excel(excel ,index_col=False)
        headers = list(df.columns)

        for id, value in df.iterrows():
            row_dict = {}
            brand_obj, brand_created = Brand.objects.get_or_create(name=value['brand'])
            cat_obj, cat_created = Category.objects.get_or_create(name=value['category'],
                                                                  sub_category=value['sub-category'])

            prod_obj = Product(name=value['name'], category=cat_obj, brand=brand_obj, model=value['model'],
                    composition=value['composition'], UOM=value['UOM'])
            prod_obj.save()

            lines.append(json.dumps({"index": {"_id": str(prod_obj.id)}}))
            lines.append(json.dumps({"name": prod_obj.name, "brand": prod_obj.brand.name, "model": prod_obj.model,
                          "category": prod_obj.category.name, "sub-category": prod_obj.category.sub_category,
                          "composition": prod_obj.composition, "UOM": prod_obj.UOM}))

            for col in headers:
                row_dict[col] = value[col]

            ret_data.append(row_dict)

        if os.path.exists("/tmp/bulk.json"):
            os.remove("/tmp/bulk.json")

        with open('/tmp/bulk.json', 'w') as file:
            file.write('\n'.join(lines))
            file.write('\n')

        op = os.system(cmd)

        return JsonResponse(json.dumps(ret_data), safe=False)

    except Exception as error:
        logger.error(error)
        logger.error(traceback.format_exc())
        return HttpResponseBadRequest(str(error))
