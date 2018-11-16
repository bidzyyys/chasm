#include <iostream>

template<class T, class Enable = void>
class A; // primary template

template<class T>
class A<T, typename std::enable_if<std::numeric_limits<T>::is_integer>::type> {
public:
    void foo() {
        std::cout << "Integer\n";
    }

};

template<class T>
class A<T, typename std::enable_if<std::is_floating_point<T>::value>::type> {
public:
    void foo() {
        std::cout << "Integer\n";
    }

};



int main() {

    A<int> a_int;
    A<double> a_d;

    a_int.foo();
    a_d.foo();

    std::cout << "Hello World!" << std::endl;
}