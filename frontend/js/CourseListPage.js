///
// frontend/js/CourseListPage.js
//
// Defines the CourseListPage class, which controls creating courses,
// deleting them, and retrieving them from the database.
//


class CourseListPage {

    constructor(serverUrl) {
        this.serverUrl = serverUrl;
        this.courses = [];
    }

    createCourse(courseData) {
        $.ajax({
            url: `${this.serverUrl}/courses/create/`,
            type: 'POST',
            cache: false,
            async: false,
            contentType: 'application/json',
            xhrFields: { withCredentials: true },
            data: JSON.stringify(courseData),
            success: function(response) {
                console.log('Course created successfully:', response);
                showMessage("Course created successfully.");
            },
            error: function(xhr, status, error) {
                console.error('Error creating course:', error);
                showMessage("Error creating course.");
            }
        });
    }

    deleteCourse(courseTitle) {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: `${this.serverUrl}/courses/${courseTitle}/delete/`,
                type: 'POST',
                cache: false,
                contentType: 'application/json',
                xhrFields: { withCredentials: true },
                success: function(response) {
                    console.log('Course deleted successfully:', response);
                    resolve(response);
                },
                error: function(xhr, status, error) {
                    console.error('Error deleting course:', error);
                    reject(error);
                }
            });
        });
    }

    loadCourses() {
        return $.ajax({
            url: `${this.serverUrl}/courses/`,
            type: 'GET',
            cache: false,
            async: false,
            contentType: 'application/json; charset=utf-8',
            xhrFields: { withCredentials: true },
            success: (response) => {
                this.courses = response.map(course => ({
                    ...course
                }));
            }
        });
    }
}

export default CourseListPage;
