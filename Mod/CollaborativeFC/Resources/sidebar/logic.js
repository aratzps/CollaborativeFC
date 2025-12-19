console.log("Social Pulse Logic Loaded");

// Notify Python that we are ready
if (window.pywebview) {
    window.pywebview.api.onUiReady();
} else {
    // Wait for the object to be injected
    window.addEventListener('pywebviewready', function () {
        window.pywebview.api.onUiReady();
    });
}

const peerList = document.getElementById('peer-list');

// Data Bridge listener (from Python)
window.updatePeers = function (peers) {
    console.log("Updating peers:", peers);
    peerList.innerHTML = '';

    peers.forEach(async peer => {
        const item = document.createElement('div');
        item.className = 'peer-item';

        let statusText = peer.status || 'Idle';
        let isMismatch = false;

        // Verify version with Python bridge
        if (window.pywebview && peer.version) {
            const result = await window.pywebview.api.validateVersion(peer.version, peer.build);
            if (result.status === 'mismatch') {
                statusText = 'VERSION MISMATCH';
                isMismatch = true;
                item.classList.add('mismatch');
            }
        }

        item.onclick = () => {
            if (window.pywebview) {
                window.pywebview.api.onPeerClick(peer.name);
            }
        };

        item.innerHTML = `
            <div class="avatar-container" style="--peer-color: ${peer.color};">
                <div class="avatar ${peer.shape || 'circle'}"></div>
                <div class="pulse ${isMismatch ? 'error' : ''}"></div>
            </div>
            <div class="peer-info">
                <span class="peer-name">${peer.name} ${isMismatch ? '⚠️' : ''}</span>
                <span class="peer-action ${isMismatch ? 'status-error' : ''}">${statusText}</span>
            </div>
        `;
        peerList.appendChild(item);
    });
};

// Session Lockdown (triggered from Python)
window.setSessionLocked = function (locked) {
    if (locked) {
        document.body.classList.add('session-locked');
        // Add a lock overlay to the sidebar
        if (!document.getElementById('lock-overlay')) {
            const overlay = document.createElement('div');
            overlay.id = 'lock-overlay';
            overlay.innerHTML = `
                <div class="lock-content">
                    <span class="lock-icon">🔒</span>
                    <span class="lock-text">Workbench Locked</span>
                </div>
            `;
            document.body.appendChild(overlay);
        }
    } else {
        document.body.classList.remove('session-locked');
        const overlay = document.getElementById('lock-overlay');
        if (overlay) overlay.remove();
    }
};
