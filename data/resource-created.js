client.test("Resource created", function() {
    client.assert(response.status === 201, "Response status is not 201");
});
