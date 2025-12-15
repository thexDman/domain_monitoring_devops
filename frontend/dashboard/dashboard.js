import { getToken, clearToken, authHeaders } from "/js/auth.js";

document.addEventListener("DOMContentLoaded", function () {

  // =======================
  // Auth Guard (CRITICAL)
  // =======================
  const token = getToken();
  if (!token) {
    window.location.href = "/login";
    return;
  }

  // =======================
  // Utility Helpers
  // =======================
  function showStatus(el, message, type = "loading") {
    if (!el) return;
    el.textContent = message;
    el.className = "";
    el.classList.add("modal-status", `status-${type}`);
  }

  async function finalizeModal(el, message, type = "success", modal, reload = true) {
    showStatus(el, message, type);
    if (type === "success" && modal) {
      setTimeout(() => {
        closeModal(modal);
        if (reload) loadDomains();
      }, 1200);
    }
  }

  function openModal(modal) {
    if (modal) modal.style.display = "flex";
  }

  function closeModal(modal) {
    if (modal) modal.style.display = "none";
  }

  // =======================
  // Global Elements
  // =======================
  const tbody = document.getElementById("domainsTableBody");

  const addDomainModal = document.getElementById("addDomainModal");
  const openAddDomainBtn = document.getElementById("openAddDomain");
  const addDomainForm = document.getElementById("addDomainForm");
  const addDomainStatus = document.getElementById("addDomainStatus");

  const bulkUploadModal = document.getElementById("bulkUploadModal");
  const openBulkUploadBtn = document.getElementById("openBulkUpload");
  const bulkUploadForm = document.getElementById("bulkUploadForm");
  const bulkUploadStatus = document.getElementById("bulkUploadStatus");

  const deleteDomainModal = document.getElementById("deleteDomainModal");
  const deleteDomainText = document.getElementById("deleteDomainText");
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");

  const logoutBtn = document.getElementById("logoutBtn");
  const scanNowBtn = document.getElementById("scanNowBtn");
  const bulkActions = document.querySelector(".bulk-actions");
  const selectAllCheckbox = document.getElementById("selectAll");

  let domainsToDelete = [];

  // =======================
  // Load & Render Domains
  // =======================
  async function loadDomains() {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-row">Loading domains…</td></tr>`;

    try {
      const res = await fetch("/api/domains", {
        headers: authHeaders()
      });

      const data = await res.json();

      if (!res.ok || !data.domains || !data.domains.length) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-row">No domains found</td></tr>`;
        return;
      }

      tbody.innerHTML = "";

      data.domains.forEach(d => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td><input type="checkbox" class="select-domain" value="${d.domain}"></td>
          <td>${d.domain}</td>
          <td><span class="badge ${d.status.toLowerCase()}">${d.status}</span></td>
          <td class="timestamp">${d.ssl_expiration}</td>
          <td>${d.ssl_issuer}</td>
          <td>
            <button class="delete-domain-btn" data-domain="${d.domain}">
              <img src="/dashboard/trash.png" class="trash-icon">
            </button>
          </td>
        `;
        tbody.appendChild(row);
      });

      attachDeleteHandlers();
      attachCheckboxHandlers();
      toggleBulkActions();

    } catch {
      tbody.innerHTML = `<tr><td colspan="6">Failed to load domains</td></tr>`;
    }
  }

  // =======================
  // Add Domain
  // =======================
  openAddDomainBtn?.addEventListener("click", () => {
    openModal(addDomainModal);
    addDomainForm.reset();
    addDomainStatus.textContent = "";
  });

  addDomainForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const domain = document.getElementById("domainInput").value.trim();

    showStatus(addDomainStatus, "Adding domain...", "loading");

    try {
      const res = await fetch("/api/domains", {
        method: "POST",
        headers: authHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({ domain })
      });

      const result = await res.json();

      if (result.ok) {
        await finalizeModal(addDomainStatus, "Domain added!", "success", addDomainModal);
      } else {
        showStatus(addDomainStatus, result.error || "Failed", "error");
      }
    } catch {
      showStatus(addDomainStatus, "Request failed", "error");
    }
  });

  // =======================
  // Bulk Upload
  // =======================
  openBulkUploadBtn?.addEventListener("click", () => {
    openModal(bulkUploadModal);
    bulkUploadForm.reset();
    bulkUploadStatus.textContent = "";
  });

  bulkUploadForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(bulkUploadForm);

    showStatus(bulkUploadStatus, "Uploading...", "loading");

    try {
      const res = await fetch("/api/domains/bulk", {
        method: "POST",
        headers: authHeaders(),
        body: formData
      });

      const result = await res.json();

      if (result.ok) {
        await finalizeModal(bulkUploadStatus, "Bulk upload completed!", "success", bulkUploadModal);
      } else {
        showStatus(bulkUploadStatus, result.error || "Upload failed", "error");
      }
    } catch {
      showStatus(bulkUploadStatus, "Upload failed", "error");
    }
  });

  // =======================
  // Delete Logic
  // =======================
  function attachDeleteHandlers() {
    document.querySelectorAll(".delete-domain-btn").forEach(btn => {
      btn.onclick = () => {
        domainsToDelete = [btn.dataset.domain];
        deleteDomainText.textContent = `Delete '${btn.dataset.domain}'?`;
        openModal(deleteDomainModal);
      };
    });
  }

  confirmDeleteBtn?.addEventListener("click", async () => {
    if (!domainsToDelete.length) return;

    showStatus(deleteDomainText, "Deleting...", "loading");

    try {
      const res = await fetch("/api/domains", {
        method: "DELETE",
        headers: authHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({ domains: domainsToDelete })
      });

      const result = await res.json();

      if (result.ok) {
        await finalizeModal(deleteDomainText, "Deleted!", "success", deleteDomainModal);
      } else {
        showStatus(deleteDomainText, "Delete failed", "error");
      }
    } catch {
      showStatus(deleteDomainText, "Request failed", "error");
    }

    domainsToDelete = [];
  });

  // =======================
  // Bulk Actions
  // =======================
  function toggleBulkActions() {
    const anyChecked = document.querySelectorAll(".select-domain:checked").length > 0;
    bulkActions.style.display = anyChecked ? "flex" : "none";
  }

  function attachCheckboxHandlers() {
    document.querySelectorAll(".select-domain").forEach(cb => {
      cb.onchange = toggleBulkActions;
    });

    selectAllCheckbox?.addEventListener("change", () => {
      document.querySelectorAll(".select-domain").forEach(cb => {
        cb.checked = selectAllCheckbox.checked;
      });
      toggleBulkActions();
    });
  }

  // =======================
  // Scan Now
  // =======================
  scanNowBtn?.addEventListener("click", async () => {
    scanNowBtn.disabled = true;
    scanNowBtn.textContent = "Scanning...";

    try {
      await fetch("/api/domains/scan", { headers: authHeaders() });
      loadDomains();
    } catch {
      alert("Scan failed");
    }

    scanNowBtn.disabled = false;
    scanNowBtn.textContent = "Scan Now";
  });

  // =======================
  // Logout
  // =======================
  logoutBtn?.addEventListener("click", e => {
    e.preventDefault();
    clearToken();
    window.location.href = "/login/";
  });

  // =======================
  // Modal Close
  // =======================
  document.querySelectorAll(".modal .close").forEach(btn => {
    btn.addEventListener("click", () => closeModal(btn.closest(".modal")));
  });

  window.addEventListener("click", e => {
    if (e.target.classList.contains("modal")) closeModal(e.target);
  });

  // =======================
  // INIT
  // =======================
  loadDomains();
});
