document.getElementById('get').addEventListener('click', async () => {
    const master = document.getElementById('master').value;
    const serviceInput = document.getElementById('service').value;
    const status = document.getElementById('status');
    
    if (!master) {
        status.innerText = "Master password required";
        status.className = "error";
        return;
    }

    let service = serviceInput;
    if (!service) {
        // Try to get domain from active tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab && tab.url) {
            try {
                const url = new URL(tab.url);
                service = url.hostname.replace('www.', '');
                document.getElementById('service').value = service;
            } catch (e) {
                console.error("Invalid URL", e);
            }
        }
    }

    status.innerText = "Connecting to bridge...";
    status.className = "";

    chrome.runtime.sendNativeMessage(
        'com.serj.password_manager',
        { action: "get", master_password: master, service: service },
        function (response) {
            if (chrome.runtime.lastError) {
                status.innerText = "Error: " + chrome.runtime.lastError.message;
                status.className = "error";
            } else if (response.status === "error") {
                status.innerText = "Error: " + response.message;
                status.className = "error";
            } else if (response.status === "success") {
                status.innerText = "Success! Autofilling...";
                status.className = "success";
                
                // Inject content script to autofill
                chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
                    chrome.scripting.executeScript({
                        target: { tabId: tabs[0].id },
                        func: (password) => {
                            const passwordFields = document.querySelectorAll('input[type="password"]');
                            if (passwordFields.length > 0) {
                                passwordFields.forEach(field => {
                                    field.value = password;
                                    field.dispatchEvent(new Event('input', { bubbles: true }));
                                    field.dispatchEvent(new Event('change', { bubbles: true }));
                                });
                                return true;
                            }
                            return false;
                        },
                        args: [response.password]
                    });
                });
            }
        }
    );
});
