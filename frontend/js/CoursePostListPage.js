
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

    formatPostContent(index, row) {
        const post = this.posts.find(p => p.id === row.id);

        return post.content;
    }

}

export default CoursePostListPage;
