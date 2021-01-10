const path = require('path');
const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql2');
const expressSanitizer = require('express-sanitizer');


const app = express();
const port = 3000;

// setting up sql database
const pool = mysql.createPool({
    host: 'localhost',
    user: 'root',
    database: 'cryptodata1',
    password: 'cake123'
});
global.db = pool.promise();


// setting the default views path to /views
app.set('views', __dirname + '/views');
app.set('view engine', 'ejs');

//rendering html files using ejs
app.engine('html', require('ejs').renderFile);
app.use(expressSanitizer());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// routes --------------------------------------------
app.use('/test', testRoutes);

// last route checked if none others satisfied - 404 - not found
app.use((req, res, next) => {
    res.status(404).render('404', {
        pageTitle: '404 Not Found'
    });
});


app.listen(port, () => console.log(`The app is listening on port ${port}`));