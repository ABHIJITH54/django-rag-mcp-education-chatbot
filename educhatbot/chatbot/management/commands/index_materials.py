from django.core.management.base import BaseCommand

from chatbot.rag import index_material
from learning.models import StudyMaterial


class Command(BaseCommand):
    help = "Index uploaded StudyMaterial PDFs into Chroma for RAG."

    def add_arguments(self, parser):
        parser.add_argument("--material-id", type=int, default=None)

    def handle(self, *args, **options):
        queryset = StudyMaterial.objects.all()
        if options["material_id"]:
            queryset = queryset.filter(id=options["material_id"])

        total_chunks = 0
        for material in queryset:
            chunks = index_material(material.id)
            total_chunks += chunks
            self.stdout.write(self.style.SUCCESS(f"Indexed {material.title}: {chunks} chunks"))

        self.stdout.write(self.style.SUCCESS(f"Done. Total chunks: {total_chunks}"))
