from werkzeug.security import generate_password_hash

users = [('user1', 'user1'),('user2', 'user2'),('user3', 'user3')]

if __name__ == "__main__":
    f = open('test_users.sql', "w")
    f.write('INSERT INTO users (username, password) VALUES\n')
    for i in range(len(users)):
        username, password = users[i]
        f.write("('%s', '%s')" % (username, generate_password_hash(password)))
        if i == len(users)-1:
            f.write(';\n')
        else:
            f.write(',\n')
