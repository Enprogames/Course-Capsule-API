///
// frontend/js/CoursePostListPage.js
//
// Defines the CoursePostListPage class, which controls creating posts,
// approving them, and retrieving a set of them from the database.
//


class CoursePostListPage {

    constructor(serverUrl, courseTitle) {
        this.serverUrl = serverUrl;
        this.courseTitle = courseTitle;
        this.courseId;
        this.courseDescription;
        this.posts = [];
    }

    loadPosts() {
        return $.ajax({
            url: `${this.serverUrl}/courses/${this.courseTitle}/posts/`,
            type: 'GET',
            async: false,
            cache: false,
            contentType: 'application/json; charset=utf-8',
            xhrFields: { withCredentials: true },
            success: (response) => {
                this.posts = response.map(post => ({
                    ...post
                }));
            }
        });
    }

    createPost(postData) {
        $.ajax({
            url: `${this.serverUrl}/courses/${this.courseTitle}/create/`,
            type: 'POST',
            cache: false,
            async: false,
            contentType: 'application/json',
            xhrFields: { withCredentials: true },
            data: JSON.stringify(postData),
            success: function(response) {
                console.log('Post created successfully:', response);
            },
            error: function(xhr, status, error) {
                console.error('Error creating course:', error);
            }
        });
    }

    approvePost(postId) {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: `${this.serverUrl}/courses/${this.courseTitle}/posts/${postId}/approve/`,
                type: 'POST',
                cache: false,
                async: false,
                contentType: 'application/json',
                xhrFields: { withCredentials: true },
                success: function(response) {
                    console.log('Post approved successfully:', response);
                    resolve(response);
                },
                error: function(xhr, status, error) {
                    console.error('Error approving post:', error);
                    reject(error);
                }
            });
        });
    }

    formatPostContent(index, row) {
        const post = this.posts.find(p => p.id === row.id);

        return post.content;
    }

}

export default CoursePostListPage;
