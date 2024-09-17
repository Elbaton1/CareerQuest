const { exec } = require("child_process");
const express = require("express");
const cron = require("node-cron");
const path = require("path");
const app = express();
const port = 3000;

// Function to run the Python scraper
function runPythonScraper() {
  exec("python scraper.py", (error, stdout, stderr) => {
    if (error) {
      console.error(`Error: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Stderr: ${stderr}`);
      return;
    }
    console.log(`Scraper Output: ${stdout}`);
  });
}

// Schedule the scraper to run every 8 hours
cron.schedule("* * * * *", () => {
  console.log("Running scraper...");
  runPythonScraper();
});

// Serve the job listings JSON from the Beans folder
app.get("/jobs", (req, res) => {
  res.sendFile(path.join(__dirname, "Beans", "job_listings.json"));
});

// Start the server
app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
