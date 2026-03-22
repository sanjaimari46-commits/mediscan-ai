const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const analyzeBtn = document.getElementById('analyzeBtn');

fileInput.addEventListener('change', function() {
    if (this.files[0]) {
        fileName.textContent = '📄 ' + this.files[0].name;
        analyzeBtn.style.display = 'block';
    }
});

async function analyzeReport() {
    const file = fileInput.files[0];
    if (!file) return;

    // Show loading
    document.getElementById('uploadBox').style.display = 'none';
    document.getElementById('loading').style.display = 'block';

    const formData = new FormData();
    formData.append('report', file);

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            resetForm();
            return;
        }

        // Show results
        document.getElementById('loading').style.display = 'none';
        document.getElementById('results').style.display = 'block';

        // Summary
        document.getElementById('summary').textContent = data.summary;

        // Normal values
        const normalList = document.getElementById('normalList');
        normalList.innerHTML = '';
        data.normal.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            normalList.appendChild(li);
        });

        // Abnormal values
        const abnormalList = document.getElementById('abnormalList');
        abnormalList.innerHTML = '';
        if (data.abnormal.length === 0) {
            abnormalList.innerHTML = '<li>No abnormal values found! 🎉</li>';
        } else {
            data.abnormal.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                abnormalList.appendChild(li);
            });
        }

        // Advice
        document.getElementById('advice').textContent = data.advice;

        // Doctor advice
        const doctorBox = document.getElementById('doctorBox');
        if (data.doctor_needed) {
            doctorBox.style.background = '#fce8e6';
            doctorBox.style.color = '#ea4335';
            document.getElementById('doctorAdvice').textContent = 
                '⚠️ Please consult a doctor regarding your abnormal values.';
        } else {
            doctorBox.style.background = '#e6f4ea';
            doctorBox.style.color = '#34a853';
            document.getElementById('doctorAdvice').textContent = 
                '✅ Your report looks good! No immediate doctor visit needed.';
        }

    } catch (error) {
        alert('Something went wrong. Please try again.');
        resetForm();
    }
}

function resetForm() {
    document.getElementById('uploadBox').style.display = 'block';
    document.getElementById('loading').style.display = 'none';
    document.getElementById('results').style.display = 'none';
    fileInput.value = '';
    fileName.textContent = '';
    analyzeBtn.style.display = 'none';
}