// UI Theme Template JavaScript

function initializeApp() {
    // Sample Form Handler
    document.getElementById('sampleForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const category = document.getElementById('category').value;
        const message = document.getElementById('message').value.trim();
        
        if (name && category) {
            // Simulate form submission
            showStatus(`Form submitted successfully! Hello, ${name}!`, 'success');
            document.getElementById('sampleForm').reset();
        } else {
            showStatus('Please fill in the required fields (Name and Category)', 'error');
        }
    });

    // Control buttons
    document.getElementById('primaryBtn').addEventListener('click', () => {
        showStatus('Primary action executed!', 'success');
        updateContentArea('primary');
    });
    
    document.getElementById('secondaryBtn').addEventListener('click', () => {
        showStatus('Secondary action executed!', 'success');
        updateContentArea('secondary');
    });
    
    document.getElementById('tertiaryBtn').addEventListener('click', () => {
        showStatus('Tertiary action executed!', 'success');
        updateContentArea('tertiary');
    });
}

function updateContentArea(action) {
    const contentArea = document.getElementById('contentArea');
    const content = {
        primary: {
            title: '🚀 Primary Action Result',
            description: 'This is the result of the primary action. You can customize this content based on your application needs.',
            details: [
                'Action executed successfully',
                'Data processed and validated',
                'Results ready for display',
                'User interface updated'
            ]
        },
        secondary: {
            title: '🔄 Secondary Action Result',
            description: 'This shows the secondary action result. The UI theme adapts to different content types seamlessly.',
            details: [
                'Secondary process completed',
                'Background tasks finished',
                'Cache updated',
                'System synchronized'
            ]
        },
        tertiary: {
            title: '💾 Tertiary Action Result',
            description: 'Tertiary action completed. The theme maintains consistency across all interactions.',
            details: [
                'Data saved successfully',
                'Backup created',
                'Logs updated',
                'Operation completed'
            ]
        }
    };

    const selectedContent = content[action];
    
    contentArea.innerHTML = `
        <div class="placeholder-content">
            <h4>${selectedContent.title}</h4>
            <p>${selectedContent.description}</p>
            <ul>
                ${selectedContent.details.map(detail => `<li>${detail}</li>`).join('')}
            </ul>
            <p><em>This content was dynamically updated at ${new Date().toLocaleTimeString()}</em></p>
        </div>
    `;
}

function showStatus(message, type) {
    const statusEl = document.getElementById('statusMessage');
    
    // Add icon based on type
    const icon = type === 'success' ? '✅ ' : '❌ ';
    statusEl.textContent = icon + message;
    statusEl.className = `status-message ${type}`;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        statusEl.style.display = 'none';
    }, 5000);
}

// Add some interactive enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects to form sections
    const formSections = document.querySelectorAll('.form-section');
    formSections.forEach(section => {
        section.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        section.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.add-btn, .control-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Add CSS for ripple animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(2);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
});