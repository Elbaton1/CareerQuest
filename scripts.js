document.addEventListener("DOMContentLoaded", function () {
  fetchJobs();
  populateFilter();
  displayTimestamp();
  fetchScrapingLog();
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

function displayJobs(jobs) {
  const jobListings = document.getElementById("job-listings");
  jobListings.innerHTML = "";

  jobs.forEach((job) => {
    const jobElement = document.createElement("div");
    jobElement.classList.add("job-listing", "col-md-4");
    jobElement.innerHTML = `
      <h2><a href="#" class="job-detail-link" data-job-id="${job.id}" data-toggle="tooltip" title="Click to view job details">${job.title}</a></h2>
      <p>${job.school}</p>
      <p>Posted on: ${job.date}</p>
      <div class="details">
        <span>${job.school}</span>
        <a href="#" class="bookmark-job" data-job-id="${job.id}"><i class="far fa-bookmark"></i></a>
        <a href="${job.link}" target="_blank">Read More</a>
      </div>
    `;
    jobListings.appendChild(jobElement);
  });

  document.querySelectorAll(".job-detail-link").forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const jobId = this.getAttribute("data-job-id");
      displayJobDetails(jobId);
    });
  });

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

function displayJobDetails(jobId) {
  fetch("Beans/job_listings.json")
    .then((response) => response.json())
    .then((data) => {
      const job = data.jobs.find((j) => j.id === jobId);
      if (job) {
        const modal = document.getElementById("jobDetailModal");
        modal.querySelector(".modal-title").textContent = job.title;
        modal.querySelector(".modal-body").innerHTML = `
          <p><strong>School:</strong> ${job.school}</p>
          <p><strong>Date Posted:</strong> ${job.date}</p>
          <p><strong>Description:</strong> ${
            job.description || "No description available."
          }</p>
          <a href="${
            job.link
          }" target="_blank" class="btn btn-primary">Apply Now</a>
        `;
        $("#jobDetailModal").modal("show");
      }
    })
    .catch((error) => {
      console.error("Error fetching job details:", error);
    });
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
      const formattedDate = formatDate(lastUpdated);
      document.getElementById(
        "timestamp"
      ).innerText = `Jobs last added on: ${formattedDate}`;
    })
    .catch((error) => {
      console.error("Error fetching last update timestamp:", error);
    });
}

function formatDate(date) {
  let hours = date.getHours();
  const minutes = date.getMinutes();
  const ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12;
  hours = hours ? hours : 12;
  const minutesStr = minutes < 10 ? "0" + minutes : minutes;
  const strTime = `${hours}:${minutesStr} ${ampm}`;
  return `${
    date.getMonth() + 1
  }/${date.getDate()}/${date.getFullYear()} ${strTime}`;
}

function fetchScrapingLog() {
  fetch("Beans/scraping_log.json")
    .then((response) => response.json())
    .then((data) => {
      displayScrapingLog(data);
    })
    .catch((error) => {
      console.error("Error fetching scraping log:", error);
    });
}

function displayScrapingLog(logs) {
  const logContainer = document.getElementById("scraping-log");
  logContainer.innerHTML = logs
    .map(
      (log) => `
    <div class="log-entry">
      <p><strong>Timestamp:</strong> ${log.timestamp}</p>
      <p><strong>New Jobs:</strong> ${log.new_jobs_count}</p>
      <p><strong>Removed Jobs:</strong> ${log.removed_jobs_count}</p>
      <details>
        <summary>Details</summary>
        <pre>${JSON.stringify(log.new_jobs, null, 2)}</pre>
        <pre>${JSON.stringify(log.removed_jobs, null, 2)}</pre>
      </details>
    </div>
  `
    )
    .join("");
}
