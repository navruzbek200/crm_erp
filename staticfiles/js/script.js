document.addEventListener("DOMContentLoaded", () => {
  // Sidebar toggle functionality
  const sidebarToggle = document.querySelector(".sidebar-toggle")
  const sidebar = document.querySelector(".sidebar")

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", () => {
      sidebar.classList.toggle("show")
    })

    // Close sidebar when clicking outside on mobile
    document.addEventListener("click", (event) => {
      if (window.innerWidth <= 768) {
        if (!sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
          sidebar.classList.remove("show")
        }
      }
    })
  }

  // Auto-submit search forms on enter
  const searchInputs = document.querySelectorAll('input[name="search"]')
  searchInputs.forEach((input) => {
    input.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        this.closest("form").submit()
      }
    })
  })

  // Add loading state to buttons
  const buttons = document.querySelectorAll(".btn")
  buttons.forEach((button) => {
    button.addEventListener("click", function () {
      if (this.type === "submit") {
        this.style.opacity = "0.7"
        this.style.pointerEvents = "none"
        setTimeout(() => {
          this.style.opacity = ""
          this.style.pointerEvents = ""
        }, 2000)
      }
    })
  })

  console.log("Fashion Store ERP loaded successfully")
})
