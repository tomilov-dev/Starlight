import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { IMDbPersonExtended } from '../../models/person.model';
import { DataService } from '../../services/data.service';

@Component({
  selector: 'app-person',
  templateUrl: './person.component.html',
  styleUrl: './person.component.css',
})
export class PersonComponent implements OnInit {
  slug: string = '';
  person: IMDbPersonExtended | undefined;

  constructor(
    private route: ActivatedRoute,
    private dataService: DataService
  ) {}

  ngOnInit(): void {
    this.slug = this.route.snapshot.params['slug'];
    this.loadPersonData();
  }

  loadPersonData() {
    this.dataService.getPerson(this.slug).subscribe({
      next: (data) => {
        console.log(data);
        this.person = data;
      },
      error: (error) => {
        console.error("Can't request person from api!", error);
      },
    });
  }
}
