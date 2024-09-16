document.addEventListener("DOMContentLoaded", function () {
  fetchJobs();
  populateFilter();
  displayTimestamp();
  fetchScrapingLog(); // This function was missing
  loadBookmarkedJobs();

  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute("href")).scrollIntoView({
        behavior: "smooth",
      });
    });
  });

  $('[data-toggle="tooltip"]').tooltip();

  const backToTopButton = document.getElementById("back-to-top");
  window.addEventListener("scroll", function () {
    if (window.scrollY > 300) {
      backToTopButton.style.display = "block";
    } else {
      backToTopButton.style.display = "none";
    }
  });
  backToTopButton.addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  const darkModeToggle = document.getElementById("dark-mode-toggle");
  darkModeToggle.addEventListener("click", function () {
    document.body.classList.toggle("dark-mode");
  });
});

function fetchJobs() {
  fetch("Beans/job_listings.json")
    .then((response) => response.json())
    .then((data) => {
      displayJobs(data.jobs);
      lazyLoadJobs();
    })
    .catch((error) => {
      console.error("Error fetching jobs:", error);
    });
}

function fetchScrapingLog() {
  fetch("Beans/scraping_log.json")
    .then((response) => response.json())
    .then((data) => {
      console.log("Scraping log data: ", data);
      // Additional logic to handle scraping log can be added here if needed
    })
    .catch((error) => {
      console.error("Error fetching scraping log:", error);
    });
}

function isJobNew(job) {
  const today = new Date();
  let jobDate;

  if (job.date) {
    jobDate = new Date(job.date);
  } else if (job.new_since) {
    jobDate = new Date(job.new_since);
  } else {
    jobDate = new Date(); // Fallback to today's date if no date is available
  }

  const diffDays = Math.floor((today - jobDate) / (1000 * 60 * 60 * 24));
  return diffDays <= 1; // Jobs posted within the last 3 days are considered new
}

// Updated displayJobs function to sort by new jobs first
function displayJobs(jobs) {
  const jobListings = document.getElementById("job-listings");
  jobListings.innerHTML = "";

  // Separate new jobs from other jobs
  const newJobs = jobs.filter(isJobNew); // Filter for new jobs
  const otherJobs = jobs.filter((job) => !isJobNew(job)); // Filter for non-new jobs

  // Combine new jobs at the top, followed by other jobs
  const sortedJobs = [...newJobs, ...otherJobs]; // New jobs come first

  // Display sorted jobs
  sortedJobs.forEach((job, index) => {
    const isNew = isJobNew(job);

    const jobElement = document.createElement("div");
    jobElement.classList.add("job-listing", "col-md-4");

    // Fallback for job id if not provided in the data
    const jobId = job.id || index;

    jobElement.innerHTML = `
      <div class="job-header">
        ${
          isNew ? '<span class="new-badge">New</span>' : ""
        } <!-- Show "New" badge if the job is new -->
        <h2><a href="${job.link}" target="_blank" class="job-title-link">${
      job.title
    }</a></h2>
      </div>
      <p>${job.school}</p>
      <p>Posted on: ${formatDisplayDate(job.date || job.new_since)}</p>
      <div class="details">
        <span>${job.school}</span>
        <a href="#" class="bookmark-job" data-job-id="${jobId}"><i class="far fa-bookmark"></i></a>
        <a href="${
          job.link
        }" target="_blank" class="read-more-link">Read More</a>
      </div>
    `;
    jobListings.appendChild(jobElement);
  });

  // Handle bookmark job functionality
  document.querySelectorAll(".bookmark-job").forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault();
      const jobId = this.getAttribute("data-job-id");
      bookmarkJob(jobId);
      this.querySelector("i").classList.toggle("fas");
      this.querySelector("i").classList.toggle("far");
    });
  });
}

function formatDisplayDate(dateString) {
  if (!dateString) {
    return "Date not provided"; // Fallback if no date is available
  }

  const date = new Date(dateString);
  if (isNaN(date.getTime())) {
    return "Date not provided"; // Fallback if the date is invalid
  }

  // Return formatted date in MM/DD/YYYY format
  return `${date.getMonth() + 1}/${date.getDate()}/${date.getFullYear()}`;
}

function bookmarkJob(jobId) {
  let bookmarkedJobs = JSON.parse(localStorage.getItem("bookmarkedJobs")) || [];
  if (bookmarkedJobs.includes(jobId)) {
    bookmarkedJobs = bookmarkedJobs.filter((id) => id !== jobId);
  } else {
    bookmarkedJobs.push(jobId);
  }
  localStorage.setItem("bookmarkedJobs", JSON.stringify(bookmarkedJobs));
}

function loadBookmarkedJobs() {
  const bookmarkedJobs =
    JSON.parse(localStorage.getItem("bookmarkedJobs")) || [];
  bookmarkedJobs.forEach((jobId) => {
    const bookmarkIcon = document.querySelector(
      `.bookmark-job[data-job-id="${jobId}"] i`
    );
    if (bookmarkIcon) {
      bookmarkIcon.classList.remove("far");
      bookmarkIcon.classList.add("fas");
    }
  });
}

function populateFilter() {
  fetch("Beans/job_listings.json")
    .then((response) => response.json())
    .then((data) => {
      const schools = Array.from(new Set(data.jobs.map((job) => job.school)));
      const filterSchool = document.getElementById("filter-school");
      filterSchool.innerHTML = `<option value="all">All Schools</option>`;
      schools.forEach((school) => {
        const option = document.createElement("option");
        option.value = school;
        option.textContent = school;
        filterSchool.appendChild(option);
      });
      filterSchool.addEventListener("change", filterJobs);
    })
    .catch((error) => {
      console.error("Error populating filter:", error);
    });
}

function searchJobs() {
  const searchInput = document.getElementById("search").value.toLowerCase();
  const filterSchool = document.getElementById("filter-school").value;

  fetch("Beans/job_listings.json")
    .then((response) => response.json())
    .then((data) => {
      let filteredJobs = data.jobs.filter((job) => {
        const matchesSearch =
          job.title.toLowerCase().includes(searchInput) ||
          job.school.toLowerCase().includes(searchInput);
        const matchesSchool =
          filterSchool === "all" || job.school === filterSchool;
        return matchesSearch && matchesSchool;
      });
      displayJobs(filteredJobs);
      lazyLoadJobs();
    })
    .catch((error) => {
      console.error("Error searching jobs:", error);
    });
}

function filterJobs() {
  const filterSchool = document.getElementById("filter-school").value;
  const searchInput = document.getElementById("search").value.toLowerCase();

  fetch("Beans/job_listings.json")
    .then((response) => response.json())
    .then((data) => {
      let filteredJobs = data.jobs.filter((job) => {
        const matchesSchool =
          filterSchool === "all" || job.school === filterSchool;
        const matchesSearch =
          job.title.toLowerCase().includes(searchInput) ||
          job.school.toLowerCase().includes(searchInput);
        return matchesSchool && matchesSearch;
      });
      displayJobs(filteredJobs);
      lazyLoadJobs();
    })
    .catch((error) => {
      console.error("Error filtering jobs:", error);
    });
}

function lazyLoadJobs() {
  const jobElements = document.querySelectorAll(".job-listing");

  const lazyLoad = (entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  };

  const observer = new IntersectionObserver(lazyLoad, {
    rootMargin: "0px",
    threshold: 0.1,
  });

  jobElements.forEach((job) => {
    observer.observe(job);
  });
}

function displayTimestamp() {
  fetch("Beans/job_listings.json")
    .then((response) => response.json())
    .then((data) => {
      const lastUpdated = new Date(data.last_updated);
      const formattedDate = formatDisplayDate(lastUpdated);
      document.getElementById(
        "timestamp"
      ).innerText = `Jobs last added on: ${formattedDate}`;
    })
    .catch((error) => {
      console.error("Error fetching last update timestamp:", error);
    });
}
