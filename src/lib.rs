pub mod primitives;

pub fn add(a: u32, b: u32) -> u32 {
    let mut sum = a;

    for i in 1..b {
        sum += i;
    }

    sum
}
