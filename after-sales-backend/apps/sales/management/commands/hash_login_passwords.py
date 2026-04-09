from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import identify_hasher, make_password
from sales.models import After_sales_index_login


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        dry_run = options["dry_run"]
        queryset = After_sales_index_login.objects.all()
        if limit > 0:
            queryset = queryset[:limit]
        total = 0
        updated = 0
        skipped = 0
        for user in queryset:
            total += 1
            password = user.password or ""
            if self._is_hashed(password):
                skipped += 1
                continue
            if dry_run:
                updated += 1
                continue
            user.password = make_password(password)
            user.save(update_fields=["password"])
            updated += 1
        self.stdout.write(
            f"scanned={total} updated={updated} skipped={skipped} dry_run={dry_run}"
        )

    def _is_hashed(self, value):
        try:
            identify_hasher(value)
            return True
        except Exception:
            return False
