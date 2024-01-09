package models;

import security.IDGenerator;

public class FantaManager {
    //#region properties
    private String id;
    public String getId() {
        return id;
    }

    private String name;
    public String getName() {
        return name;
    }

    private String password;
    public String getPassword() { return password; }

    private String email;
    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }
    //#endregion

    //#region constructors
    public FantaManager(String name, String email, String password) {
        this.id = IDGenerator.randomStringUUID();
        this.name = name;
        this.email = email;
        this.password = password;
    }
    //#endregion

    //#region methods
    public void update(String name, String email) {
        this.name = name;
        this.email = email;
    }

    public void delete() {
        this.id = null;
        this.name = null;
        this.email = null;
    }

    @Override
    public String toString() {
        return  name + "[id= " + id + ", email= " + email + "]";
    }
    //#endregion
}
