
echo "Starting scraper..."

# Make script executable if not already
chmod +x Scraper.py

# Install required packages if missing
if ! python3 -c "import selenium" &> /dev/null; then
    echo "Installing selenium..."
    pip install selenium
fi

# Run the specialized scraper
python3 Scraper.py

echo "Scraper finished."
