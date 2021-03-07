#include<iostream>
#include<string>
#include<vector>
#include<deque>
#include<list>
#include<math.h>


using namespace std;

class Person{
    public:
        string p_name;
        int p_age;
        Person(string name, int age);
};

Person::Person(string name, int age){
    this->p_age = age;
    this->p_name = name;
}

void vector_test(){
    vector<Person> v;
    Person p1("alice", 19);
    Person p2("bob", 13);

    v.push_back(p1);
    v.push_back(p2);
    // v.insert
    

    for (vector<Person>::iterator i = v.begin(); i!=v.end(); i++){
        cout<<"这个人的名字是："<<(*i).p_age<<endl;
    }
}

void deque_test(){
    deque<Person> d;
    Person p1("alice", 19);
    Person p2("bob", 13);
    d.push_back(p1);
    d.push_back(p2);

    for (deque<Person>::iterator i = d.begin(); i!=d.end(); i++){
        cout<<"说人名："<<(*i).p_name<<endl;
    }
}


void list_test()
{
    list<int> li1;
    for (int i=0;i<5;i++){
        li1.push_back(pow(i,2));
    }

    for(list<int>::iterator i = li1.begin(); i != li1.end(); i++){
        cout<< *i << " ";
    }
    cout<<endl;
    // cout<<li1[3];
}



int main(){
    // vector_test();
    // deque_test();
    list_test();
    system("pause");
    return 0;
}