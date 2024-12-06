/* static/js/create_petition.js */

/*jshint esversion: 8 */

document.addEventListener("DOMContentLoaded", async function () {
    let selectedCategory = null;
    const progressBar = document.getElementById('progressBar');
    const steps = document.querySelectorAll('.step');

    // Length limiting: https://github.com/sparksuite/simplemde-markdown-editor/issues/584#issuecomment-346965224
    const simplemde = new SimpleMDE({
        element: document.getElementById("description"), status: [{
            className: "chars",
            defaultValue: function (el) {
                el.innerHTML = "0 / " + 1024;
            },
            onUpdate: function (el) {
                el.innerHTML = simplemde.value().length + " / " + 1024;
                limit_characters();
            }
        }]
    });

    // Length limiting continued
    function limit_characters() {
        document.getElementById('submitForm').classList.add('d-none');
        if (simplemde.value().length > 1024) {
            document.getElementById("showMockup").disabled = true
        } else {
            document.getElementById("showMockup").disabled = false
        }
    }

    // Toggle the visibility of each step
    function showStep(step) {
        steps.forEach((stepElement, index) => {
            if (index + 1 === step) {
                stepElement.classList.remove('d-none');
            } else {
                stepElement.classList.add('d-none');
            }
        });
    }

    // Toggle the selection state of each button (ensuring only one can be selected)
    function updateButtonState() {
        document.querySelectorAll('.category-option button').forEach(btn => {
            if (btn.getAttribute('data-category') === selectedCategory) {
                btn.classList.add('selected');
            } else {
                btn.classList.remove('selected');
            }
        });
    }

    // Render the mockup card of the petition with the specified data
    function generateMockupCard(data) {
        const mockupContainer = document.getElementById('mockupContainer');

        // Was easier to override the innerHTML that use the card component
        mockupContainer.innerHTML = `
            <div class="col-md-12 mb-4">
                <div class="card text-decoration-none text-dark">
                    <div class="row no-gutters">
                        <div class="col-md-8">
                            <div class="card-body">
                                <span class="badge badge-primary">Draft</span>
                                <span class="badge badge-warning">Waiting</span>
                                <span class="badge badge-info">${data.category}</span>
                                <h5 class="card-title mt-2">${data.title}</h5>
                                <div class="card-text">${data.tag_line}</div>
                            </div>
                            <div class="card-footer d-flex justify-content-between">
                                <small class="text-muted">By Anonymous</small>
                                <small class="text-muted">Just Now • 0 signatures</small>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <img src="${data.image_url || 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTJTcLeoDwmVmpJHNs8Ni9-4MHDhcFDQ-yr-g&s'}" class="card-img" alt="${data.title}">
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Validate image to ensure it can be loaded
    // Derived from: https://stackoverflow.com/questions/20613984/jquery-or-javascript-check-if-image-loaded
    function validateImage(imageURL) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve();
            img.onerror = () => reject();
            img.src = imageURL;
        });
    }

    // Store the category of the last selected button
    document.querySelectorAll('.category-option button').forEach(button => {
        button.addEventListener('click', function () {
            selectedCategory = this.getAttribute('data-category');
            document.getElementById('category').value = selectedCategory;
            updateButtonState();
            document.getElementById('nextStep1').disabled = false;
        });
    });

    // Show step 2 and adjust the progress bars percentage
    document.getElementById('nextStep1').addEventListener('click', function () {
        showStep(2);
        progressBar.style.width = '33%';
    });

    // Ensure the title input has content before allowing them to progress to the next step
    document.getElementById('title').addEventListener('input', function () {
        document.getElementById('nextStep2').disabled = this.value.trim().length < 3;
    });

    // Show step 3 and adjust the progress bars percentage
    document.getElementById('nextStep2').addEventListener('click', function () {
        showStep(3);
        progressBar.style.width = '66%';
    });

    // Show step 1 and adjust the progress bar percentage
    document.getElementById('prevStep2').addEventListener('click', function () {
        showStep(1);
        progressBar.style.width = '0%';
        updateButtonState();
    });

    // Show step 2 and adjust the progress bar percentage
    document.getElementById('prevStep3').addEventListener('click', function () {
        showStep(2);
        progressBar.style.width = '33%';
        document.getElementById('submitForm').classList.add('d-none');
        document.getElementById('mockupContainer').innerHTML = "";
    });

    // Handle mockup generation
    document.getElementById('showMockup').addEventListener('click', async function (event) {
        // Getting the raw description from simplemde (The markdown editor)
        const descriptionValue = simplemde.value();
        document.getElementById('description').value = descriptionValue;

        // Utilising SweetAlert2
        if (descriptionValue.length < 3) {
            display([['success', "ERRTOAST|Please provide a description"]]);
            return;
        }

        const tagLine = document.getElementById('tag_line').value;

        if (tagLine.length < 3) {
            display([['success', "ERRTOAST|Please provide a tag line"]]);
            return;
        }

        const imageURL = document.getElementById('image_url').value;

        if (imageURL.length > 0) {
            // Regular expression from: https://regexr.com/39nr7 (Google Query: "valid url regex")
            const isValidURL = imageURL.match('[(http(s)?):\\/\\/(www\\.)?a-zA-Z0-9@:%._\\+~#=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%_\\+.~#?&//=]*)');

            if (!isValidURL) {
                display([['success', "ERRTOAST|Please provide a valid URL"]]);
                return;
            }

            try {
                // Wait for the image validation to complete
                await validateImage(imageURL);
            } catch (error) {
                display([['success', "ERRTOAST|Error loading the specified image"]]);

                return;
            }
        }

        // Generate a JS form object and store it on the petitionForm object 
        // https://developer.mozilla.org/en-US/docs/Web/API/FormData/FormData
        const formData = new FormData(document.getElementById('createPetitionForm'));
        let petitionData = {};
        formData.forEach((value, key) => {
            petitionData[key] = value;
        });
        petitionData['category'] = selectedCategory;

        generateMockupCard(petitionData);
        document.getElementById('submitForm').classList.remove('d-none');
    });

    // Re-render the preview if the description is updated and hide submit button
    document.getElementById('tag_line').addEventListener('input', function () {
        document.getElementById('submitForm').classList.add('d-none');
    });

});

