import click

from otica_scripts.config import MAX_MESSAGE_LENGTH, WHATSAPP_PROVIDER
from otica_scripts.evolution_sender import EvolutionSender
from otica_scripts.message_tracker import MessageManager
from otica_scripts.scraper import GoogleSearchScraper
from otica_scripts.store import StoreManager
from otica_scripts.whatsapp_sender import WhatsAppSender


@click.group()
def cli() -> None:
    """Ótica Price Finder - Send WhatsApp messages to multiple glasses stores."""
    pass


@cli.command()
@click.option("--name", required=True, help="Store name")
@click.option("--phone", required=True, help="Phone number (e.g., +5511999999999)")
@click.option("--address", default=None, help="Store address (optional)")
def add_store(name: str, phone: str, address: str | None) -> None:
    """Add a new store to the database."""
    manager = StoreManager()
    store = manager.add_store(name, phone, address)
    click.echo(f"Added store: {store.name} ({store.phone})")


@cli.command()
@click.argument("name")
def remove_store(name: str) -> None:
    """Remove a store from the database."""
    manager = StoreManager()
    if manager.remove_store(name):
        click.echo(f"Removed store: {name}")
    else:
        click.echo(f"Store not found: {name}")


@cli.command()
def list_stores() -> None:
    """List all stores in the database."""
    manager = StoreManager()
    stores = manager.get_all_stores()
    if not stores:
        click.echo("No stores found. Add some stores first!")
        return
    for store in stores:
        address = f" - {store.address}" if store.address else ""
        click.echo(f"  {store.name}: {store.phone}{address}")


@cli.command()
@click.argument("message")
@click.option("--dry-run", is_flag=True, help="Show which stores would receive the message")
@click.option("--test", "test_mode", is_flag=True, help="Send to only 1 store (for testing)")
@click.option(
    "--provider",
    type=click.Choice(["playwright", "evolution"]),
    default=WHATSAPP_PROVIDER,
    help="Which provider to use for sending (default from env)",
)
def send(message: str, dry_run: bool, test_mode: bool, provider: str) -> None:
    """Send a message to all stores."""
    if len(message) > MAX_MESSAGE_LENGTH:
        click.echo(f"Error: Message exceeds {MAX_MESSAGE_LENGTH} characters")
        return
    manager = StoreManager()
    msg_tracker = MessageManager()
    stores = manager.get_all_stores()

    if test_mode:
        stores = stores[:1]
        click.echo("[TEST MODE] Sending to only 1 store...")
    elif dry_run:
        click.echo(f"Would send to {len(stores)} stores:")
        for store in stores:
            click.echo(f"  - {store.name}: {store.phone}")
        return

    if not stores:
        click.echo("No stores found. Add some stores first!")
        return

    click.echo(f"\n{'='*50}")
    click.echo("SENDING MESSAGES")
    click.echo(f"{'='*50}")
    click.echo(f"Total stores: {len(stores)}")
    click.echo(f"Message: {message[:50]}...")
    click.echo(f"Provider: {provider}")
    click.echo(f"{'='*50}\n")

    if provider == "evolution":
        sender: EvolutionSender | WhatsAppSender = EvolutionSender()
    else:
        sender = WhatsAppSender()

    try:
        click.echo("\nOpening WhatsApp Web...")
        whatsapp_ok = sender.open_whatsapp()

        if not whatsapp_ok:
            click.echo("\n❌ FAILED: Could not connect to WhatsApp Web")
            if provider == "playwright":
                click.echo("Please make sure:")
                click.echo("  1. You're connected to the internet")
                click.echo("  2. QR code was scanned successfully")
                click.echo("  3. Try again\n")
            else:
                click.echo("Please make sure:")
                click.echo("  1. Docker containers are running (docker-compose up -d)")
                click.echo("  2. You scanned the QR code via terminal")
                click.echo("  3. API Key is correct\n")
            return

        results = sender.send_to_all(stores, message)

        click.echo(f"\n{'='*50}")
        click.echo("RESULTS")
        click.echo(f"{'='*50}")

        success_count = 0
        failed_stores = []

        for store in stores:
            success = results.get(store.name, False)
            status = "✅ SENT" if success else "❌ FAILED"
            click.echo(f"{status} | {store.name} | {store.phone}")

            if success:
                msg_tracker.add_message(store.name, store.phone, message)
                success_count += 1
            else:
                failed_stores.append(store.name)

        click.echo(f"\n{'='*50}")
        click.echo(f"SUMMARY: {success_count}/{len(stores)} sent successfully")

        if failed_stores:
            click.echo(f"Failed stores: {', '.join(failed_stores)}")

        click.echo(f"{'='*50}\n")

    finally:
        sender.close()


@cli.command()
@click.option("--location", default="ótica Santarém Pará Brasil", help="Location to search")
@click.option("--add", is_flag=True, help="Automatically add found stores to database")
def scrape(location: str, add: bool) -> None:
    """Scrape optical stores from Google Search."""
    click.echo(f"Scraping Google for: {location}")
    scraper = GoogleSearchScraper()
    try:
        results = scraper.scrape_optical_stores(location)
        click.echo(f"\nFound {len(results)} stores:")
        for store in results:
            phone = store.get("phone", "No phone")
            address = store.get("address", "")
            addr_str = f" - {address}" if address else ""
            click.echo(f"  {store['name']}: {phone}{addr_str}")

        if add and results:
            manager = StoreManager()
            added_count = 0
            for store in results:
                if store.get("phone"):
                    try:
                        manager.add_store(
                            name=store["name"],
                            phone=store["phone"],
                            address=store.get("address")
                        )
                        added_count += 1
                    except Exception as e:
                        click.echo(f"  Error adding {store['name']}: {e}")
            click.echo(f"\nAdded {added_count} stores to database")
    finally:
        scraper.close()


@cli.command()
@click.argument("csv_file", type=click.Path(exists=True))
def import_csv(csv_file: str) -> None:
    """Import stores from a CSV file."""
    import csv

    manager = StoreManager()
    added_count = 0

    with open(csv_file, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('name', '').strip()
            phone = row.get('phone', '').strip()
            address = row.get('address', '').strip() or None

            if name and phone:
                try:
                    manager.add_store(name, phone, address)
                    added_count += 1
                    click.echo(f"  Added: {name} - {phone}")
                except Exception as e:
                    click.echo(f"  Error adding {name}: {e}")

    click.echo(f"\nAdded {added_count} stores to database")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
