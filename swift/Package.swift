// swift-tools-version:5.7
import PackageDescription

let package = Package(
    name: "N4V3R41N",
    platforms: [
        .macOS(.v10_15)
    ],
    products: [
        .executable(name: "n4v3r41n", targets: ["N4V3R41N"])
    ],
    dependencies: [
        .package(url: "https://github.com/apple/swift-argument-parser", from: "1.2.0"),
    ],
    targets: [
        .executableTarget(
            name: "N4V3R41N",
            dependencies: [
                .product(name: "ArgumentParser", package: "swift-argument-parser"),
            ],
            path: "Sources/N4V3R41N"
        )
    ]
)
