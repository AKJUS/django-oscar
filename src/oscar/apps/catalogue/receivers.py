# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import connection
from django.db.models.signals import post_delete, post_save, m2m_changed
from django.dispatch import receiver

from oscar.core.loading import get_model
from oscar.checks import use_productcategory_materialised_view

Category = get_model("catalogue", "Category")
ProductCategory = get_model("catalogue", "ProductCategory")


if settings.OSCAR_DELETE_IMAGE_FILES:
    from django.db import models

    from oscar.core.thumbnails import get_thumbnailer

    ProductImage = get_model("catalogue", "ProductImage")

    # pylint: disable=unused-argument
    def delete_image_files(sender, instance, **kwargs):
        """
        Deletes the original image and created thumbnails.
        """
        image_fields = (models.ImageField,)
        thumbnailer = get_thumbnailer()
        for field in instance._meta.fields:
            if isinstance(field, image_fields):
                # Make Django return ImageFieldFile instead of ImageField
                field_file = getattr(instance, field.name)
                thumbnailer.delete_thumbnails(field_file)

    # Connect for all models with ImageFields - add as needed
    models_with_images = [ProductImage, Category]
    for image_instance in models_with_images:
        post_delete.connect(delete_image_files, sender=image_instance)


# pylint: disable=unused-argument
@receiver(post_save, sender=Category, dispatch_uid="set_ancestors_are_public")
def post_save_set_ancestors_are_public(sender, instance, **kwargs):
    if kwargs.get("raw"):
        return

    instance.set_ancestors_are_public()


@receiver([post_save, post_delete, m2m_changed], sender=ProductCategory)
def refresh_materialized_view(sender, **kwargs):
    if kwargs.get("raw") or not use_productcategory_materialised_view():
        return

    with connection.cursor() as cursor:
        cursor.execute(
            "REFRESH MATERIALIZED VIEW CONCURRENTLY catalogue_product_category_hierarchy;"
        )
