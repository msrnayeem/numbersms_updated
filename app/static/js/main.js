window.addEventListener("DOMContentLoaded", function () {
  // navbar scroll fixed
  const navbar = this.document.getElementById("navbar");
  if (navbar) {
    this.window.addEventListener("scroll", function () {
      if (this.scrollY > 0) {
        navbar.classList.add("fixed");
      } else {
        navbar.classList.remove("fixed");
      }
    });
  }

  // mobile menu toggler
  const mobileMenuToggler = document.getElementById("mobileMenuToggler");
  const mobileMenu = document.getElementById("mobileMenu");
  let mobileMenuStatus = false;
  if (mobileMenuToggler && mobileMenu) {
    mobileMenuToggler.addEventListener("click", () => {
      if (!mobileMenuStatus) {
        mobileMenu.classList.remove("opacity-0", "pointer-events-none");
        mobileMenu.querySelector("ul").classList.remove("translate-x-[-100%]");
        mobileMenuStatus = true;
      } else {
        mobileMenu.classList.add("opacity-0", "pointer-events-none");
        mobileMenu.querySelector("ul").classList.add("translate-x-[-100%]");
        mobileMenuStatus = false;
      }
    });

    mobileMenu.addEventListener("click", function () {
      if (mobileMenuStatus) {
        this.classList.add("opacity-0", "pointer-events-none");
        this.querySelector("ul").classList.add("translate-x-[-100%]");
        mobileMenuStatus = false;
      }
    });
  }

  // dashboard sidebar collaps
  const sidebar = document.getElementById("sidebar");
  const sidebarcollapsbtn = document.querySelectorAll("#sidebarcollapsbtn");
  let sidebarcollaps = false;
  if (sidebar && sidebarcollapsbtn) {
    sidebarcollapsbtn.forEach((btn) => {
      btn.addEventListener("click", function () {
        if (!sidebarcollaps) {
          sidebar.classList.remove("left-[-100%]");
          sidebarcollaps = true;
        } else {
          sidebar.classList.add("left-[-100%]");
          sidebarcollaps = false;
        }
      });
    });
  }


  // admin =============
  // proifle
  const profilebtn = document.getElementById("profilebtn");
  const profilemenu = document.getElementById("profilemenu");
  if (profilebtn && profilemenu) {
    profilebtn.addEventListener("click", () => {
      profilemenu.classList.toggle("pointer-events-none");
      profilemenu.classList.toggle("translate-y-10");
      profilemenu.classList.toggle("opacity-0");
    });
  }
});
