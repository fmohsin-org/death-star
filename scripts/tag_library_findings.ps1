$javaUuids = @(
    "69d12e414d93d8d6a8af65d2",
    "69d12e414d93d8d6a8af65d3",
    "69d12e415525eedabeef7044",
    "69d12e415525eedabeef7045",
    "69d12e417330dcd7deddf13c",
    "69d12e419101298ae464dae3",
    "69d12e419101298ae464dae6",
    "69d12e419101298ae464dae7",
    "69d12e419101298ae464dae9",
    "69d12e41b67b09c0a88b31f3",
    "69d12e41b67b09c0a88b31f5",
    "69d12e41ec2ef820ed03b7d1",
    "69d12e41ec2ef820ed03b7d2",
    "69d12e41ec2ef820ed03b7d4",
    "69d12ea74d93d8d6a8af9cba",
    "69d12ea7b67b09c0a88b68e7",
    "69d313907330dcd7de6b50c9",
    "69d313907585ee258df5c3c8"
)

$goUuids = @(
    "69d12e477330dcd7deddf5bf",
    "69d12e479101298ae464df62",
    "69d12e487330dcd7deddf5c0",
    "69d317044d93d8d6a83e52e8",
    "69d317045525eedabe7e5eb9",
    "69d317045525eedabe7e5eba",
    "69d3170459970cc319ca3e94",
    "69d317047330dcd7de6ce284",
    "69d317047330dcd7de6ce285",
    "69d317049101298ae4f3c585",
    "69d317049101298ae4f3c586",
    "69d31704ec2ef820ed92a0a6",
    "69d31704ec2ef820ed92a0a7"
)

$pyUuids = @(
    "69d12e154d93d8d6a8af53c3",
    "69d12e154d93d8d6a8af53c4",
    "69d12e154d93d8d6a8af53c5",
    "69d12e154d93d8d6a8af53c6",
    "69d12e155525eedabeef5e1d",
    "69d12e155525eedabeef5e1e",
    "69d12e157330dcd7dedddf0b",
    "69d12e157330dcd7dedddf0e",
    "69d12e159101298ae464c8c3",
    "69d12e159101298ae464c8c5",
    "69d12e15b67b09c0a88b1fc4",
    "69d12e15b67b09c0a88b1fc6",
    "69d12e15b67b09c0a88b1fc7",
    "69d12e609101298ae464ee41",
    "69d12e609101298ae464ee42",
    "69d12e60b67b09c0a88b454e",
    "69d318855525eedabe7ed9bf",
    "69d318857330dcd7de6d5d77"
)

Write-Host "=== Tagging Java library findings ($(($javaUuids).Count)) ==="
$i = 0
foreach ($uuid in $javaUuids) {
    $i++
    endorctl api update --resource Finding -n auri --uuid $uuid --field-mask 'meta.tags' --data '{"meta":{"tags":["cross-repo-sast","cross-repo-sast-java"]}}' --output-type yaml 2>$null | Out-Null
    Write-Host "  [$i/$($javaUuids.Count)] Tagged $uuid"
}

Write-Host "`n=== Tagging Go library findings ($(($goUuids).Count)) ==="
$i = 0
foreach ($uuid in $goUuids) {
    $i++
    endorctl api update --resource Finding -n auri --uuid $uuid --field-mask 'meta.tags' --data '{"meta":{"tags":["cross-repo-sast","cross-repo-sast-go"]}}' --output-type yaml 2>$null | Out-Null
    Write-Host "  [$i/$($goUuids.Count)] Tagged $uuid"
}

Write-Host "`n=== Tagging Python library findings ($(($pyUuids).Count)) ==="
$i = 0
foreach ($uuid in $pyUuids) {
    $i++
    endorctl api update --resource Finding -n auri --uuid $uuid --field-mask 'meta.tags' --data '{"meta":{"tags":["cross-repo-sast","cross-repo-sast-python"]}}' --output-type yaml 2>$null | Out-Null
    Write-Host "  [$i/$($pyUuids.Count)] Tagged $uuid"
}

Write-Host "`n=== Done! Verifying total tagged findings ==="
endorctl api list --resource Finding -n auri --filter 'meta.tags contains ["cross-repo-sast"]' --count
