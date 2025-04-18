async function httpRequest(url, method = "GET", data = null, headers = {}) {
  try {
    let options = {
      method,
      headers: { "Content-Type": "application/json", ...headers },
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    let response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("HTTP Request Failed:", error);
    return null;
  }
}

function modelhandler(target, afteropen = null, afterclose = null) {
  if (target) {
    const model = document.getElementById(target);
    const model_body = model.querySelector("#model_body");

    if (
      model_body.classList.contains("scale-50") &&
      model_body.classList.contains("opacity-0") &&
      model_body.classList.contains("pointer-events-none")
    ) {
      model_body.classList.remove(
        "scale-50",
        "opacity-0",
        "pointer-events-none"
      );
      if (typeof afteropen === "function" && afteropen.length > 0) {
        afteropen(model);
      } else if (typeof afteropen === "function") {
        afteropen();
      }
    } else {
      model_body.classList.add("scale-50", "opacity-0", "pointer-events-none");
      if (typeof afteropen === "function" && afteropen.length > 0) {
        afterclose(model);
      } else if (typeof afteropen === "function") {
        afterclose();
      }
    }

    setTimeout(() => {
      if (
        model.classList.contains("opacity-0") &&
        model.classList.contains("pointer-events-none")
      ) {
        model.classList.remove("opacity-0", "pointer-events-none");
      } else {
        model.classList.add("opacity-0", "pointer-events-none");
      }
    }, 100);
  }
}
